import json
from unittest.mock import patch
from django.test import TestCase, TransactionTestCase, override_settings
from django.urls import reverse
from django.conf import settings
from django.core import mail
from cart.cart import Cart
from listings.models import Listing
from .models import Order


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


class SimpleOrderTestCase(OrderTestCase, TestCase):
    def test_order_number(self):
        """
        Generate random order number, ensure length and format
        """
        number = Order.objects.generate_number()
        self.assertRegex(number, r'^(?:\d{4}-?){3}$')

    def test_404(self):
        """
        Accessing the order views with an empty cart should raise a 404
        """
        session = self.client.session
        del session['CART']
        session.save()
        response = self.client.get(reverse('shop:order'))
        self.assertEqual(response.status_code, 404)

    def test_404_session(self):
        """
        Views that rely on order info saved in session should raise a 404
        """
        session = self.client.session
        session[self.key] = None
        response = self.client.get(reverse('shop:review'))
        self.assertEqual(response.status_code, 404)

    def test_404_token(self):
        """
        Incorrect order token should raise 404
        """
        response = self.client.get(
            reverse('shop:status', kwargs={'token': 'xxxx'})
        )
        self.assertEqual(response.status_code, 404)


class CreateOrderTestCase(OrderTestCase, TestCase):
    def test_order_get(self):
        response = self.client.get(reverse('shop:order'))
        self.assertEqual(response.context['action'], reverse('shop:order'))

    def test_order_post(self):
        response = self.client.post(reverse('shop:order'), data=self.data)
        order = Order.objects.first()
        self.assertEqual(order.first_name, 'Test')
        self.assertEqual(response.status_code, 302)
        self.assertIn(Listing.objects.first(), order.listing_set.all())
        self.assertEqual(self.client.session[self.key]['number'], order.number)
        self.assertEqual(
            self.client.session[self.key]['status'],
            Order.Status.UNPAID
        )

    def test_update_order_get(self):
        self.client.post(reverse('shop:order'), data=self.data)
        response = self.client.get(reverse('shop:update'))
        self.assertEqual(response.context['action'], reverse('shop:update'))


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

    @patch('shop.tasks.customer_order_notification')
    @patch('common.tasks.notify_admins')
    @patch('square.client.Client.payments')
    def test_successful_charge_view(self, mock_client, *args):
        mock_client.create_payment.is_success.return_value = True
        mock_client.create_payment.body.return_value = {
            'payment': {
                'square_payment_id': 'xxx',
                'square_order_id': 'xxx',
                'receipt_number': 'xxx',
                'receipt_url': 'https://example.com'
            }
        }
        # TODO fix exception with Mock and db
        response = self.client.post(
            reverse('shop:charge'),
            data=json.dumps({'nonce': '123456'}),
            content_type='application/json'
        )
        # Successful order redirects to order status page
        self.assertURLEqual(
            response.json()['url'], self.order.get_absolute_url()
        )

    @patch('shop.tasks.customer_order_notification')
    @patch('common.tasks.notify_admins')
    @patch('square.client.Client.payments')
    def test_unsuccessful_charge_view(self, mock_client, *args):
        """
        Missing nonce should cancel order
        """
        mock_client.create_payment.is_success.return_value = False
        response = self.client.post(
            reverse('shop:charge'),
            data=json.dumps({'nonce': None}),
            content_type='application/json'
        )
        # Order is canceled and user is redirected to index view
        self.assertEqual(self.order.status, Order.Status.CANCELED)
        self.assertURLEqual(
            response.json()['url'], reverse('index')
        )

    def test_invoice_view(self):
        response = self.client.get(
            reverse('shop:invoice', kwargs={'token': self.order.token()})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get('Content-Disposition'),
            'inline; filename="invoice.pdf"'
        )

    def test_resent_email(self):
        self.client.get(
            reverse('shop:resend', kwargs={'token': self.order.token()})
        )
        self.assertEqual(len(mail.outbox), 1)

    @patch('shop.models.Order.soft_delete')
    def test_cancel_order(self, mock_delete):
        response = self.client.post('shop:cancel')
        self.assertRedirects(response, reverse('index'))
        self.assertTrue(mock_delete.called)
