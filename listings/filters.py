from django_filters import FilterSet
from django_filters.filters import CharFilter, NumberFilter
from .models import Listing


class ListingFilter(FilterSet):
    category = CharFilter(
        lookup_expr='iexact',
        field_name='category__name',
        method='filter_unsold'
    )
    price__lte = NumberFilter(
        lookup_expr='lte',
        field_name='price'
    )
    materials = CharFilter(
        lookup_expr='icontains',
        method='filter_unsold'
    )

    def filter_unsold(self, queryset, name, value):
        return queryset.unsold().filter(**{name: value})

    class Meta:
        model = Listing
        fields = ['category', 'price']
