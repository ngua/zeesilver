import time
from django.test import TestCase, override_settings
from django.urls import reverse
from django.conf import settings
from cart.cart import Cart, ListingUnavailable
from listings.models import Listing


class CartTestCase(TestCase):
    """
    Load the test fixtures from the listings app
    """
    fixtures = ['listings/fixtures/listings.yaml']


class CartSessionTestCase(CartTestCase):
    def test_cart_add_remove_item(self):
        """
        Test basic cart functionality
        """
        listing = Listing.objects.get(pk=1)
        session = self.client.session
        cart = Cart(session)
        cart.add(listing)
        self.assertIsNotNone(cart)
        self.assertFalse(cart.is_empty)
        self.assertIn(listing.pk, cart)
        self.assertTrue(listing.sold)
        self.assertEqual(1, cart.count)
        #  Test if adding an item already in the cart raises exception
        try:
            cart.add(listing)
        except ListingUnavailable:
            pass
        cart.remove(listing)
        self.assertTrue(cart.is_empty)
        self.assertNotIn(listing.pk, cart.items)
        self.assertFalse(listing.sold)

    def test_session_storage(self):
        """
        Test if session stores serialized cart items and removes them
        when the cart is cleared
        """
        listing = Listing.objects.get(pk=1)
        session = self.client.session
        cart = Cart(session)
        cart.add(listing)
        self.assertIsNotNone(session[cart.KEY])
        self.assertIn(listing.pk, session[cart.KEY])
        cart.clear()
        self.assertFalse(session[cart.KEY])

    def test_cart_raises(self):
        """
        Test raising an exception by trying to add a sold Listing instance to
        a different session cart
        """
        listing = Listing.objects.get(pk=1)
        session = self.client.session
        cart1 = Cart(session)
        cart1.add(listing)
        # Change the session dictionary to create a different cart object
        session.update({
            'session_key': 'test',
            Cart.KEY: []
        })
        cart2 = Cart(session)
        self.assertNotEqual(cart1, cart2)
        # Try to raise an exception by adding a Listing instance that is
        # already in a cart
        with self.assertRaises(ListingUnavailable):
            cart2.add(listing)


class CartViewTestCase(CartTestCase):
    def test_cart_add_remove_view(self):
        """
        Test that cart add/remove views successfully store and update
        serialized carts in session dictionary, and redirect properly
        """
        listing = Listing.objects.get(pk=1)
        response = self.client.post(
            reverse('cart-add'), {'listing': listing.slug}
        )
        self.assertRedirects(response, '/')
        session = self.client.session
        self.assertIn(listing.pk, session[Cart.KEY])

        # Test if removing an item with a non-empty cart correctly redirects
        # back to the cart status view
        listing2 = Listing.objects.get(pk=2)
        self.client.post(
            reverse('cart-add'), {'listing': listing2.slug}
        )
        response = self.client.post(
            reverse('cart-remove'), {'listing': listing.slug}
        )
        self.assertRedirects(response, reverse('cart'))

        # Clear cart and redirect back to index view
        response = self.client.post(
            reverse('cart-remove'), {'listing': listing2.slug}
        )
        self.assertRedirects(response, '/')

    def test_cart_status_view(self):
        """
        Test that clients can retrieve and view stored cart data
        """
        # Add item first
        listing = Listing.objects.get(pk=1)
        self.client.post(
            reverse('cart-add'), {'listing': listing.slug}
        )
        response = self.client.get(reverse('cart'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'$', response.content)

    def test_cart_clear_view(self):
        listing = Listing.objects.get(pk=1)
        self.client.post(
            reverse('cart-add'), {'listing': listing.slug}
        )
        self.client.post(reverse('cart-clear'))
        session = self.client.session
        cart = Cart(session)
        self.assertFalse(cart.items)
        self.assertFalse(session[Cart.KEY])

    def test_bad_post_redirect(self):
        """
        Test if adding non-existent Listing raises Http404 exception
        """
        response = self.client.post(
            reverse('cart-add'), {'listing': ''}
        )
        self.assertEqual(response.status_code, 404)


class CartMiddlewareTestCase(CartTestCase):
    """
    Test the cart timeout Middleware
    """
    def test_timestamp(self):
        """
        Test that timestamp to measure activity is stored in session
        """
        session_key = settings.CART_TIMEOUT_KEY
        self.client.get('/')
        session = self.client.session
        self.assertTrue(session[session_key])
        self.assertLess(session[session_key], time.time())

    @override_settings(CART_TIMEOUT=0)
    def test_cart_timeout(self):
        """
        Tests the CartTimeOutMiddleware to ensure that carts are automatically
        cleared when clients have been inactive. Overrides the CART_TIMEOUT
        setting to simulate exceeding the maximum period of inactivity allowed
        """
        # Add listing to cart
        listing = Listing.objects.get(pk=1)
        self.client.post(
            reverse('cart-add'), {'listing': listing.slug}
        )
        # Attempt to view cart
        response = self.client.get(reverse('cart'))
        self.assertIn(b'Your cart was automatically cleared', response.content)
        session = self.client.session
        cart = Cart(session)
        self.assertFalse(cart.items)
