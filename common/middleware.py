from django.conf import settings
from django.shortcuts import redirect, reverse
from django.contrib import messages
from django.core.exceptions import MiddlewareNotUsed
from django.contrib.gis.geoip2.base import GeoIP2Exception
from django.contrib.gis.geoip2 import GeoIP2
from geoip2.errors import AddressNotFoundError
from ipware import get_client_ip


class GeoIPMiddleware:
    """
    Middleware to detect client ip and redirect from restricted views if
    necessary. The merchant currently can only process payments and ship to a
    small number of countries; due to the nature of the inventory, it is best
    if clients from non-supported countries cannot place items in carts or
    attempt to place an order
    As GeoIP databases are imprecise and incomplete, if the Middelware cannot
    determine client country, the view function is either executed or passed
    to the next middleware as configured in the settings

    TODO Add C mmdb library; decouple GeoIP2 instance from wsgi app and into
    dedicated service with own memory
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.whitelist = getattr(settings, 'GEO_WHITELIST', ('US',))
        self.restricted_views = getattr(settings, 'GEO_RESTRICTED_VIEWS', [])
        self.proxy_trusted_ips = getattr(settings, 'PROXY_TRUSTED_IPS', [])
        self.proxy_count = getattr(settings, 'PROXY_COUNT', [])
        self.key = getattr(settings, 'GEO_KEY', 'GEOIP')
        # Try to initialize the GeoIP instance when the server starts to avoid
        # instantiating it for every request.
        try:
            self.geoip = GeoIP2()
        except GeoIP2Exception:
            raise MiddlewareNotUsed('GeoIP2 data failed to load')

    def __call__(self, request):
        # Save the session for `process_view`
        self.session = request.session
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        # If the view is not in the restricted list, return immediately to
        # execute any view functions or pass them to subsequent middlewares
        if view_func.__module__ not in self.restricted_views:
            return

        # Including proxy parameters helps mitigate client IP spoofing to some
        # degree; good practice even if this middleware is not used for
        # something truly critical
        if settings.DEBUG:
            client_ip, is_routable = get_client_ip(request)
        else:
            client_ip, is_routable = get_client_ip(
                request,
                proxy_count=self.proxy_count,
                proxy_trusted_ips=self.proxy_trusted_ips
            )
        # If client's ip can't be established, or is private, etc, return and
        # call view function rather than spuriously redirecting. This also
        # prevents repeatedly making invalid queries later
        if client_ip is None or not is_routable:
            return

        data = self.session.get(self.key)
        country = self.verify_country(data, client_ip)
        if country is not None and country not in self.whitelist:
            # If the country has been established and is not in whitelist,
            # flash message about shipping and payment policy and redirect to
            # homepage
            messages.warning(
                request,
                (
                    'Zeesilver is currently only able to accept payment '
                    'from and offer shipping to customers in the US. We '
                    'apologize for any inconvenience.'
                )
            )
            return redirect(reverse('index'))
        return

    def verify_country(self, data, client_ip):
        """
        Checks the session for existing client data. If the country has not
        previously been stored in the session, checks the GeoIP database.
        Returns either the country code or None.
        """
        if data is None:
            country = self.get_country_code(client_ip)
            # Store client data in session to retrive it on next request,
            # rather than calling an expensive GeoIP method on each request
            self.update(country, client_ip)
        else:
            stored_country, stored_ip = data
            # If ip has changed, update the session with new ip and country
            if stored_ip != client_ip:
                country = self.get_country_code(client_ip)
                self.update(client_ip, country)
            else:
                return stored_country
        return country

    def get_country_code(self, client_ip):
        """
        Query the GeoIP database to determine client country. If location
        cannot be determined, returns None
        """
        try:
            return self.geoip.country(client_ip).get('country_code')
        except AddressNotFoundError:
            return

    def update(self, client_ip, country):
        """
        Inserts a list with the client ip and country into the session
        dictionart
        """
        self.session[self.key] = [client_ip, country]
