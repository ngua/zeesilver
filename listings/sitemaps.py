from django.contrib.sitemaps import Sitemap
from .models import Listing


class ListingSiteMap(Sitemap):
    change_freq = 'monthly'
    priority = 0.7

    def items(self):
        return Listing.objects.unsold()

    def lastmod(self, obj):
        return obj.created
