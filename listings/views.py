from django.views.generic import DetailView
from django.http import Http404
from django_filters.views import FilterView
from .models import Listing
from .filters import ListingFilter


class ListingFilterView(FilterView):
    filterset_class = ListingFilter
    queryset = Listing.objects.unsold()
    paginate_by = 6

    def get_context_data(self, *args, **kwargs):
        """
        Includes some additional context to conditionally
        render elements in the template, e.g. add css styles
        to currently selected filter/combination. `price__lte`
        needs to be case to an int to compare it with the price
        point context processor (Moneyfield instances)
        """
        price = self.request.GET.get('price__lte', '')
        category = self.request.GET.get('category', '')
        order = self.request.GET.get('order_by', '-price')
        if price and price.isnumeric():
            price = int(price)

        context = super().get_context_data(*args, **kwargs)
        context.update({
            'current_category': category,
            'current_price': price,
            'current_order': order
        })
        return context


class ListingDetailView(DetailView):
    model = Listing

    def get_object(self):
        """
        Overriding parent method to ensure that items marked as
        sold can no longer be accessed. Each inventory item is unique,
        so it's best if the DetailView only shows unsold items
        """
        obj = super().get_object()
        if obj.sold:
            raise Http404
        return obj

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['related'] = self.object.get_related()
        return context
