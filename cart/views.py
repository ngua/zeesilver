from django.views import View
from django.contrib import messages
from django.http import Http404, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from listings.models import Listing
from .cart import Cart, ListingUnavailable


class CartViewMixin(View):
    http_method_names = ['get', 'post']

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.cart = Cart(self.request.session)


class CartAddView(CartViewMixin):
    def post(self, request, *args, **kwargs):
        slug = self.request.POST.get('listing')
        try:
            listing = Listing.objects.get(slug=slug)
        except (Listing.DoesNotExist, ListingUnavailable):
            raise Http404
        self.cart.add(listing)
        messages.success(
            request,
            f'{listing.name} has been added to your cart'
        )
        return HttpResponseRedirect(reverse('index'))


class CartRemoveView(CartViewMixin):
    def post(self, request, *args, **kwargs):
        slug = self.request.POST.get('listing')
        listing = Listing.objects.get(slug=slug)
        self.cart.remove(listing)
        messages.info(
            request,
            f'{listing.name} has been removed from your cart'
        )
        if self.cart.is_empty:
            return HttpResponseRedirect(reverse('index'))
        return HttpResponseRedirect(reverse('cart'))


class CartStatusView(CartViewMixin):
    template_name = 'cart/status.html'

    def get(self, request, *args, **kwargs):
        return TemplateResponse(request, self.template_name, {})


class CartClearView(CartViewMixin):
    def post(self, request, *args, **kwargs):
        self.cart.clear()
        messages.info(request, 'Your cart has been cleared')
        return HttpResponseRedirect(reverse('index'))
