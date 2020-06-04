from django.http import HttpResponseServerError
from django.conf import settings
from merchant.models import SquareConfig


class ShopAvailableMiddleware:
    """
    Verifies that a Square Connect OAuth token exists to ensure that payments
    can be made in shop views. Raises 500 response if no Square OAuth
    configuration exists.

    Intended as a fallback to guarantee that malformed payment attempts aren't
    sent to Square endpoints
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.shop_views = getattr(settings, 'SHOP_VIEWS', ('shop.views',))

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        if view_func.__module__ not in self.shop_views:
            return
        # Only instantiate the SquareConfig singleton if view is included
        # in settings to avoid overhead on every view
        square_config = SquareConfig.get_solo()
        if not square_config.active:
            return HttpResponseServerError()
        return
