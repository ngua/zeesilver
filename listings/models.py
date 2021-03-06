import secrets
from django.db import models, transaction
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify
from django.db.models import signals
from django.dispatch import receiver
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from djmoney.models.fields import MoneyField
from ckeditor.fields import RichTextField
from .managers import CategoryManager, ListingManager


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    objects = CategoryManager()

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __repr__(self):
        return f"Category('{self.name}')"

    def __str__(self):
        return self.name


class Material(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __repr__(self):
        return f"Model('{self.name}')"

    def __str__(self):
        return self.name


def listing_upload_path(instance, filename):
    return f'{settings.LISTING_MEDIA}/{instance.slug}_{filename}'


class Listing(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = RichTextField()
    picture = models.ImageField(upload_to=listing_upload_path)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    materials = models.ManyToManyField(Material, blank=True)
    pieces = models.IntegerField(default=1)
    price = MoneyField(max_digits=14, decimal_places=2, default_currency='USD')
    created = models.DateField(default=timezone.now)
    sold = models.BooleanField(default=False)
    slug = models.SlugField(editable=False)
    order = models.ForeignKey(
        'shop.Order', null=True, blank=True, on_delete=models.SET_NULL
    )
    search_vector = SearchVectorField(null=True, blank=True, editable=False)

    objects = ListingManager()

    class Meta:
        indexes = [GinIndex(fields=['search_vector'])]
        ordering = ['-price']

    def get_absolute_url(self):
        return reverse(
            'listing:detail',
            kwargs={
                'category': self.category.name.lower(),
                'slug': self.slug
            }
        )

    def save(self, *args, **kwargs):
        """
        Overrides `save` in order to:
        1. Generate a slug once, ensuring that name changes do not
        affect existing slug, otherwise existing URLs might 404
        2. Call a celery tasks to update the instance's `search_vector`
        by aggregating newly saved data, updating the field, and then re-
        saving the instance, making sure that `save` is not being called
        specifically to update the search vector
        """
        if not self.id:
            slug = slugify(self.name)
            # Ensure that slug is unique
            if self.__class__.objects.filter(slug=slug).exists():
                while True:
                    # Use random token to avoid exposing application internals
                    # to clients (i.e., by using instance pk)
                    token = secrets.token_urlsafe(4)
                    slug += token
                    if not self.__class__.objects.filter(slug=slug).exists():
                        break
            self.slug = slug
        super().save(*args, **kwargs)
        if 'search_vector' not in kwargs.get('update_fields', {}):
            from .tasks import update_search
            # 'on_commit' necessary to avoid race condition between
            # Django and Celery when accessing model instance
            # NOTE Remember that TransactionTestCase is needed for tests
            transaction.on_commit(
                lambda: update_search.delay(self.pk)
            )

    def get_related(self, limit=10):
        """
        Returns list of Listing objects with the same category
        as the instance, for use in detail view sidebar
        """
        return Listing.objects.exclude(id=self.id).filter(
            category=self.category
        ).select_related('category').defer('search_vector').unsold()[:limit+1]

    def __repr__(self):
        return f"Listing('{self.name}', '{self.category}')"

    def __str__(self):
        return self.name


@receiver(signals.post_delete, sender=Listing)
def auto_delete_picture(sender, instance, **kwargs):
    instance.picture.delete(save=False)


# The following signals call the instance `save` method to update the search
# vector when related objects are updated

@receiver(signals.post_save, sender=Category)
def category_updated(sender, instance, **kwargs):
    for listing in instance.listing_set.query_summary():
        listing.save()


@receiver(signals.post_save, sender=Material)
def materials_updated(sender, instance, **kwargs):
    for listing in instance.listing_set.query_summary():
        listing.save()


@receiver(signals.m2m_changed, sender=Listing.materials.through)
def update_materials_m2m(sender, instance, action, **kwargs):
    if action in ['post_save', 'post_clear', 'post_add']:
        instance.save()
