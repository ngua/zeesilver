from django.db import models
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify
from django.db.models import signals, TextField, Value as V
from django.db import transaction
from django.db.models.functions import Concat
from django.dispatch import receiver
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField, SearchVector
from django.contrib.postgres.aggregates import StringAgg
from djmoney.models.fields import MoneyField
from ckeditor.fields import RichTextField


class CategoryQuerySet(models.QuerySet):
    def in_stock(self):
        """
        Returns all Category instances with at least one unsold related
        Listing object
        """
        return self.filter(listing__sold=False).distinct()


class CategoryManager(models.Manager):
    def get_queryset(self):
        return CategoryQuerySet(self.model, using=self._db)

    def in_stock(self):
        return self.get_queryset().in_stock()

    def get_example_listings(self):
        """
        Yields one example Listing instance for each category
        with at least one unsold related Listing. For use in
        the index view
        """
        for category in self.in_stock().distinct():
            yield category.listing_set.unsold().first()


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


class ListingQuerySet(models.QuerySet):
    def unsold(self):
        return self.filter(sold=False)


class ListingManager(models.Manager.from_queryset(ListingQuerySet)):
    def generate_summary(self):
        """
        Creates a field for aggregating all text fields into a single
        searchable value. Postgres' SearchVector cannot include joined
        fields since it uses Django's F expression, so this step is
        necessary to search Listing through the Category and Material `name`
        attributes in the Listing SearchVectorField.
        Since this is a rather computationally intensive task, it shouldn't
        be called in the ListingManager `get_queryset` method directly,
        otherwise it will affect all Listing db calls
        """
        return self.get_queryset().annotate(
            summary=Concat(
                'name', V(' '),
                'description', V(' '),
                'category__name', V(' '),
                StringAgg('materials__name', delimiter=' '),
                output_field=TextField()
            )
        )

    def query_summary(self):
        """
        Adds the annotated `summary` value to the queryset. For
        use in the Listing `save` method for post-save search
        vector update
        """
        vector = (
            SearchVector('name', weight='A') +
            SearchVector('description', weight='C') +
            SearchVector('category__name', weight='B') +
            SearchVector(StringAgg(
                'materials__name', delimiter=' '
            ), weight='A')
        )
        return self.generate_summary().annotate(summary=vector)

    def unsold(self):
        return self.get_queryset().unsold()


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
    search_vector = SearchVectorField(null=True)

    objects = ListingManager()

    class Meta:
        indexes = [GinIndex(fields=['search_vector'])]
        ordering = ['-price']

    def get_absolute_url(self):
        return reverse(
            'listing-detail',
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
        saving, the instance, making sure that `save` is not being called
        specifically to update the search vector
        """
        if not self.id:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        if 'search_vector' not in kwargs.get('update_fields', {}):
            from .tasks import update_search_task
            # 'on_commit' necessary to avoid race condition between
            # Django and Celery when accessing model instance
            # NOTE Remember that TransactionTestCase is needed for tests
            transaction.on_commit(
                lambda: update_search_task.delay(self.pk)
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
