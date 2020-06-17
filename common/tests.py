from django.test import TestCase
from django.urls import reverse
from listings.models import Listing
from cart.cart import Cart


class IndexTestCase(TestCase):
    def test_get(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)


class GeoIPTestCase(TestCase):
    fixtures = ['listings/fixtures/listings.yaml']

    def setUp(self):
        self.listing = Listing.objects.first()
        self.cart = Cart(self.client.session)

    def test_ip_fail(self):
        self.client.post(
            reverse('cart:add'), {'listing': self.listing.slug},
            # Non-US IP address
            REMOTE_ADDR='2.57.168.1'
        )
        self.assertNotIn(self.listing.pk, self.cart)

    def test_ip_pass(self):
        self.client.post(
            reverse('cart:add'), {'listing': self.listing.slug},
            # US IP address
            REMOTE_ADDR='199.187.211.102'
        )
        self.assertIn(self.listing.pk, self.cart)
