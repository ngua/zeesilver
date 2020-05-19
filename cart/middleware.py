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

    # Cart expiry in seconds, default one hour
    TIMEOUT = getattr(settings, 'CART_TIMEOUT', 3600)
    KEY = getattr(settings, 'CART_TIMEOUT_KEY', 'CART_TIMEOUT')

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """
        Instantiate the cart using the session and check check the epoch
        timestamp, clearing the cart and redirecting if expired, otherwise
        refreshing the timestamp

        NOTE Since the session is modified directly, this also has the side
        effect of resetting the session cookie expiry
        """
        response = self.get_response(request)
        timestamp = request.session.setdefault(self.KEY, time.time())

        cart = Cart(request.session)

        if not cart.is_empty:
            if time.time() - timestamp > self.TIMEOUT:
                cart.clear()
                messages.warning(
                    request,
                    'Your cart was automatically cleared due to inactivity'
                )

        request.session[self.KEY] = time.time()
        return response
