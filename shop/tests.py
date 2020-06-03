import json
from unittest.mock import patch
from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from django.conf import settings
from cart.cart import Cart
from listings.models import Listing
from .models import Order


class SimpleOrderTestCase(TestCase):
    def test_404(self):
        """
        Accessing the order views with an empty cart should raise
        a 404
        """
        response = self.client.get(reverse('shop:order'))
        self.assertEqual(response.status_code, 404)

    def test_order_number(self):
        number = Order.objects.generate_number()
        self.assertRegex(
            number,
            r'\d{4}-\d{4}-\d{4}'
        )


class OrderTestCase:
    fixtures = ['listings/fixtures/listings.yaml']
    key = getattr(settings, 'ORDER_KEY', 'ORDER')

    def setUp(self):
        listing = Listing.objects.first()
        session = self.client.session
        self.cart = Cart(session)
        self.cart.add(listing)
        session.save()

        self.data = {
            'first_name': 'Test',
            'last_name': 'Test',
            'email': 'test@test.com',
            'phone': '(555) 555-5555',
            'street_address': '123 Test St',
            'city': 'Test',
            'state': 'AK',
            'zip_code': '55555'
        }


class CreateOrderTestCase(OrderTestCase, TransactionTestCase):
    def test_order_view(self):
        response = self.client.post(
            reverse('shop:order'),
            data=self.data
        )
        order = Order.objects.first()
        self.assertEqual(
            order.first_name,
            'Test'
        )
        self.assertEqual(
            response.status_code,
            302
        )
        self.assertIn(
            Listing.objects.first(),
            order.listing_set.all()
        )
        self.assertEqual(
            self.client.session[self.key]['number'],
            order.number
        )
        self.assertEqual(
            self.client.session[self.key]['status'],
            Order.Status.UNPAID
        )


class OrderFlowTestCase(OrderTestCase, TransactionTestCase):
    def setUp(self):
        super().setUp()
        self.order = Order.objects.create(**self.data)
        self.order.add_from_cart(self.cart)
        session = self.client.session
        session[self.key] = self.order.serialize()
        session.save()

    def test_review_view(self):
        response = self.client.get(reverse('shop:review'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.order.address)

    def test_payment_view(self):
        response = self.client.get(reverse('shop:pay'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.order.total)

    @patch('square.client.Client.payments')
    def test_charge_view(self, mock_client):
        mock_client.create_payment.is_success.return_value = True
        mock_client.create_payment.body.return_value = {
            'payment': {
                'square_payment_id': 'xxx',
                'square_order_id': 'xxx',
                'receipt_number': 'xxx',
                'receipt_url': 'https://example.com'
            }
        }
        response = self.client.post(
            reverse('shop:charge'),
            data=json.dumps({'nonce': '123456'}),
            content_type='application/json'
        )
