import time
from django.conf import settings
from django.urls import reverse
from django.shortcuts import redirect
from django.http import HttpResponseServerError
from django.contrib import messages
from merchant.models import SquareConfig
from cart.cart import Cart
from .utils import cancel_order
from .models import Order


class ShopBaseMiddleware:
    """
    Common Middleware attributes for shop views
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.shop_views = getattr(settings, 'SHOP_VIEWS', ('shop.views',))

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        raise NotImplementedError


class ShopAvailableMiddleware(ShopBaseMiddleware):
    """
    Verifies that a Square Connect OAuth token exists to ensure that payments
    can be made in shop views. Raises 500 response if no Square OAuth
    configuration exists.

    Intended as a fallback to guarantee that malformed payment attempts aren't
    sent to Square endpoints
    """
    def process_view(self, request, view_func, view_args, view_kwargs):
        if view_func.__module__ not in self.shop_views:
            return
        # Only instantiate the SquareConfig singleton if view is included
        # in settings to avoid overhead on every view
        square_config = SquareConfig.get_solo()
        if not square_config.active:
            return HttpResponseServerError()
        return


class OrderTimeoutMiddleware(ShopBaseMiddleware):
    """
    Ensures that order is completed within given timeframe. Checks the order
    status and timestamp
    """
    def __init__(self, get_response):
        super().__init__(get_response)
        self.key = getattr(settings, 'ORDER_KEY', 'ORDER')
        self.timeout = getattr(settings, 'ORDER_TIMEOUT', 3600)

    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Retrieves timestamps from the session, compares to current time, and
        either returns or cancels order if limit has been exceeded
        """
        if view_func.__module__ not in self.shop_views:
            return

        session = request.session
        # Make sure that order has already been placed
        if self.key not in session:
            return

        now = time.time()
        active = session[self.key].get('active')
        status = session[self.key].get('status')

        if now - active > self.timeout and status == Order.Status.UNPAID:
            order_number = session[self.key].get('number')
            order = Order.objects.get(number=order_number)
            cart = Cart(session)
            if order is not None:
                cancel_order(order, cart, self.key, session)
            messages.error(
                request, 'Your order has been canceled due to inactivity'
            )
            return redirect(reverse('index'))

        return
