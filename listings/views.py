from django.views.generic import DetailView
from django_filters.views import FilterView
from .models import Listing
from .filters import ListingFilter


class ListingFilterView(FilterView):
    filterset_class = ListingFilter

    def get_context_data(self, *args, **kwargs):
        current_price = self.request.GET.get('price__lte', '')
        category = self.request.GET.get('category', '')
        if current_price and current_price.isnumeric():
            current_price = int(current_price)
        context = super().get_context_data(*args, **kwargs)
        context.update({
            'current': category,
            'current_price': current_price
        })
        return context


class ListingDetailView(DetailView):
    model = Listing

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['related'] = self.object.get_related()
        return context
