from django.db.models import F
from django.views.generic import ListView
from django.contrib.postgres.search import SearchQuery, SearchRank
from listings.models import Listing


class SearchListView(ListView):
    model = Listing
    template_name = 'search/results.html'
    paginate_by = 10

    def get_queryset(self):
        q = self.request.GET.get('q', '')
        qs = Listing.objects.unsold()

        if q:
            query = SearchQuery(q)
            qs = qs.annotate(
                rank=SearchRank(
                    F('search_vector'), query
                )).filter(search_vector=query).order_by('-rank')

        self.q = q
        self.total = len(qs)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'q': self.q,
            'total': self.total
        })
        return context
