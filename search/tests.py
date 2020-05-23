from django.test import TestCase
from django.urls import reverse
from listings.models import Listing


class SearchTestCase(TestCase):
    """
    Load the test fixtures from the listings app
    """
    fixtures = ['listings/fixtures/listings.yaml']


class SearchViewTest(SearchTestCase):
    def test_get_request(self):
        response = self.client.get(reverse('search'))
        self.assertEqual(response.status_code, 200)

    def test_search_filter(self):
        # Broad search, should contain several fixture listings
        response = self.client.get(reverse('search'), {'q': 'silver'})
        print(response.context)
        self.assertGreater(len(response.context['object_list']), 1,)
        # Should only return the one Listing instance
        response = self.client.get(reverse('search'), {'q': 'amethyst'})
        results = response.context['object_list']
        self.assertEqual(len(results), 1)
        self.assertIn(Listing.objects.get(pk=2), results)
