from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticSiteMap(Sitemap):
    priority = 0.6
    changefreq = 'monthly'

    def items(self):
        return ['index', 'contact']

    def location(self, item):
        return reverse(item)
