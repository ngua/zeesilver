from django_filters import FilterSet
from django_filters.filters import CharFilter, NumberFilter, OrderingFilter
from .models import Listing


class ListingFilter(FilterSet):
    category = CharFilter(lookup_expr='iexact', field_name='category__name')
    price__lte = NumberFilter(lookup_expr='lte', field_name='price')
    materials = CharFilter(lookup_expr='icontains')
    order_by = OrderingFilter(fields=(('price', 'price'),))

    class Meta:
        model = Listing
        fields = ['category', 'price']
