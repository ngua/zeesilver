from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.views.generic import CreateView, View
from cart.cart import Cart
from .models import Order
from .forms import OrderForm


class OrderMixin(View):
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.cart = Cart(self.request.session)


class CancelOrderMixin(OrderMixin):
    def post(self, request, *args, **kwargs):
        if 'cancel' in request.POST:
            self.cart.clear()
            messages.info(request, 'Your order has been cancelled')
            return redirect(reverse('index'))
        return super().post(request, *args, **kwargs)


class OrderCreateView(CancelOrderMixin, CreateView):
    model = Order
    form_class = OrderForm
    success_url = reverse_lazy('shop:review')


class PaymentView(CancelOrderMixin):
    pass
