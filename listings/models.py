from django.db import models
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify
from django.db.models import signals
from django.dispatch import receiver
from django.contrib.postgres.fields import ArrayField
from djmoney.models.fields import MoneyField
from ckeditor.fields import RichTextField


class CategoryQuerySet(models.QuerySet):
    def in_stock(self):
        return self.filter(
            listing__isnull=False
        ).exclude(listing__sold=True)


class CategoryManager(models.Manager):
    def get_queryset(self):
        return CategoryQuerySet(self.model, using=self._db)

    def in_stock(self):
        return self.get_queryset().in_stock()

    def get_example_listings(self):
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


class ListingQuerySet(models.QuerySet):
    def unsold(self):
        return self.filter(sold=False)


class ListingManager(models.Manager):
    def get_queryset(self):
        return ListingQuerySet(self.model, using=self._db)

    def unsold(self):
        return self.get_queryset().unsold()


def listing_upload_path(instance, filename):
    return f'{settings.LISTING_MEDIA}/{instance.slug}_{filename}'


class Listing(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = RichTextField()
    picture = models.ImageField(upload_to=listing_upload_path)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    materials = ArrayField(models.CharField(max_length=100))
    pieces = models.IntegerField(default=1)
    price = MoneyField(max_digits=14, decimal_places=2, default_currency='USD')
    created = models.DateField(default=timezone.now)
    sold = models.BooleanField(default=False)
    slug = models.SlugField(editable=False)

    objects = ListingManager()

    def get_absolute_url(self):
        return reverse(
            'listing-detail',
            kwargs={
                'category': self.category.name.lower(),
                'slug': self.slug
            }
        )

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __repr__(self):
        return f"Listing('{self.name}', '{self.category}')"

    def __str__(self):
        return self.name


@receiver(signals.post_delete, sender=Listing)
def auto_delete_picture(sender, instance, **kwargs):
    instance.picture.delete(save=False)
