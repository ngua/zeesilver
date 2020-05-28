from django.db import models
from django.db.models.functions import Concat
from django.db.models import Value as V, TextField
from django.contrib.postgres.search import SearchVector
from django.contrib.postgres.aggregates import StringAgg


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
