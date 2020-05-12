from django.views.generic import ListView, DetailView
from .models import Listing, Category


class ListingByCategoryListView(ListView):
    model = Listing

    def get_queryset(self):
        qs = super().get_queryset()
        category = self.request.GET.get('category', '')
        qs = qs.filter(
            category__name__iexact=category
        )
        return qs.unsold()

    def get_context_data(self, *args, **kwargs):
        response = super().get_context_data(*args, **kwargs)
        response['categories'] = Category.objects.in_stock().distinct()
        response['current'] = self.request.GET.get('category', '')
        return response


class ListingDetailView(DetailView):
    model = Listing
