import time
from django.contrib import messages
from django.conf import settings
from .cart import Cart


class CartTimeoutMiddleware:
    """
    Middleware to set cart timeout in sessions. Since all Listing instances are
    unique, they should not be placed in carts indefinitely. This middleware
    ensures that items in inactive carts are returned to stock after a
    reasonable delay
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # Cart expiry in seconds, default one hour
        self.timeout = getattr(settings, 'CART_TIMEOUT', 3600)
        # Key to store serialized cart items in session
        self.key = getattr(settings, 'CART_TIMEOUT_KEY', 'CART_TIMEOUT')

    def __call__(self, request):
        """
        Instantiate the cart using the session and check check the epoch
        timestamp, clearing the cart and redirecting if expired, otherwise
        refreshing the timestamp

        NOTE Since the session is modified directly, this also has the side
        effect of resetting the session expiry
        """
        response = self.get_response(request)
        timestamp = request.session.setdefault(self.key, time.time())

        cart = Cart(request.session)

        if not cart.is_empty:
            if time.time() - timestamp > self.timeout:
                cart.clear()
                messages.warning(
                    request,
                    'Your cart was automatically cleared due to inactivity'
                )

        request.session[self.key] = time.time()
        return response
