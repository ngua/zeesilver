from django.views import View
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib import messages
from django.http import Http404
from django.template.response import TemplateResponse
from django.utils.safestring import mark_safe
from listings.models import Listing
from .cart import Cart, ListingUnavailable


def emphasize(listing_name):
    return f'<em>{listing_name}</em>'


class CartViewMixin(View):
    http_method_names = ['get', 'post']
    redirect_url = '/'

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.cart = Cart(self.request.session)


class CartAddView(CartViewMixin):
    def post(self, request, *args, **kwargs):
        slug = self.request.POST.get('listing')
        try:
            listing = Listing.objects.get(slug=slug)
            self.cart.add(listing)
        except (Listing.DoesNotExist, ListingUnavailable):
            raise Http404()
        messages.success(
            request,
            mark_safe(
                f'{emphasize(listing.name)} has been added to your cart'
            )
        )
        return redirect(self.redirect_url)


class CartRemoveView(CartViewMixin):
    def post(self, request, *args, **kwargs):
        slug = self.request.POST.get('listing')
        listing = Listing.objects.get(slug=slug)
        self.cart.remove(listing)
        messages.info(
            request,
            mark_safe(
                f'{emphasize(listing.name)} has been removed from your cart'
            )
        )
        if self.cart.is_empty:
            return redirect(self.redirect_url)
        return redirect(reverse('cart'))


class CartStatusView(CartViewMixin):
    template_name = 'cart/status.html'

    def get(self, request, *args, **kwargs):
        return TemplateResponse(request, self.template_name, {})


class CartClearView(CartViewMixin):
    def post(self, request, *args, **kwargs):
        self.cart.clear()
        messages.info(request, 'Your cart has been cleared')
        return redirect(self.redirect_url)
