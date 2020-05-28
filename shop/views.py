import json
from uuid import uuid4
from collections import OrderedDict
from django.conf import settings
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.http import Http404, JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.core.signing import BadSignature
from django.views.generic import (
    View, CreateView, DetailView, DeleteView, UpdateView
)
from django.views.generic.base import ContextMixin
from square.client import Client
from cart.cart import Cart
from .models import Order, Payment
from .forms import OrderForm
from .utils import cancel_order


class OrderProgressMixin(ContextMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            # Add checkout steps to context for users to see progress
            'steps': OrderedDict([
                ('Shipping Information', 'OrderCreateView'),
                ('Review Your Order', 'ReviewOrderView'),
                ('Payment', 'PaymentView'),
                ('Success!', 'OrderStatusView'),
            ]),
            # Get current view name to style with CSS in template
            'current': self.__class__.__name__
        })
        return context


class OrderMixin(OrderProgressMixin, View):
    http_method_names = ['get', 'post']

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.key = getattr(settings, 'ORDER_KEY', 'ORDER')
        self.cart = Cart(self.request.session)

    def dispatch(self, request, *args, **kwargs):
        """
        Ensures that a non-empty cart exists for the current session
        """
        if self.cart.is_empty:
            raise Http404()
        return super().dispatch(request, *args, **kwargs)


class OrderSessionMixin(OrderMixin):
    """
    Retrieves serialized order from session
    """
    queryset = Order.objects.all()

    def get_object(self):
        """
        Tries to retrieve Order instance from serialized representation in the
        session, raising 404 if not found
        """
        order = self.request.session.get(self.key)
        if order is None:
            raise Http404('No Order Found')
        number, _ = order.values()
        return self.queryset.get(number=number)


class OrderCreateView(OrderMixin, CreateView):
    form_class = OrderForm
    success_url = reverse_lazy('shop:review')
    template_name = 'shop/order_form.html'

    def get_context_data(self, **kwargs):
        """
        Adds view url for form action (form is generic)
        """
        context = super().get_context_data(**kwargs)
        context['action'] = reverse('shop:order')
        return context

    def form_valid(self, form):
        """
        Add items from session cart to order listing set
        """
        form.instance.save()
        form.instance.add_from_cart(self.cart)
        # Save a representation of the order in the session
        self.request.session[self.key] = form.instance.serialize()
        return super().form_valid(form)


class ReviewOrderView(OrderSessionMixin, DetailView):
    pass


class UpdateOrderView(OrderSessionMixin, UpdateView):
    form_class = OrderForm
    success_url = reverse_lazy('shop:review')
    template_name = 'shop/order_update_form.html'

    def get_context_data(self, **kwargs):
        """
        Sets the current view for CSS styling in progress bar and adds action
        to generic form in template
        """
        context = super().get_context_data(**kwargs)
        context.update({
            'current': 'OrderCreateView',
            'action': reverse('shop:update')
        })
        return context


class PaymentView(OrderSessionMixin, DetailView):
    template_name = 'shop/pay.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'square_application_id': settings.SQUARE_APPLICATION_ID,
            'payment_url': reverse('shop:charge'),
            'amount': self.object.total,
            'square_payment_library': settings.SQUARE_PAYMENT_LIBRARY
        })
        return context


class ChargeView(OrderMixin):
    http_method_names = ['post']

    def setup(self, request, *args, **kwargs):
        """
        Tries to fetch the order from the session.  This is not an generic
        editing view, so OrderSessionMixin is not appropriate.
        """
        super().setup(request, *args, **kwargs)
        order = request.session.get(self.key)
        if order is None:
            raise Http404()
        number, _ = order.values()
        self.order = get_object_or_404(Order, number=number)
        self.client = Client(
            access_token=settings.SQUARE_ACCESS_TOKEN,
            environment=settings.SQUARE_ENVIRONMENT
        )

    def get_success_url(self):
        return self.order.get_absolute_url()

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        nonce = data.get('nonce')
        if nonce is None:
            return self.charge_invalid()

        currency, amount = self.order.units()
        idempotency_key = str(uuid4())
        body = {
            'source_id': nonce,
            'idempotency_key': idempotency_key,
            'amount_money': {
                'currency': currency,
                'amount': amount
            }
        }
        result = self.client.payments.create_payment(body)
        if result.is_success():
            return self.charge_valid(result)
        else:
            return self.charge_invalid()

    def charge_valid(self, result):
        session = self.request.session
        Payment.objects.from_response(result, self.order)
        self.object.finalize(session)
        return JsonResponse({
            'url': self.get_success_url(),
        })

    def charge_invalid(self):
        cancel_order(
            instance=self.order,
            cart=self.cart,
            key=self.key,
            session=self.request.session
        )
        return JsonResponse({'url': reverse('index')})


class OrderStatusView(OrderProgressMixin, DetailView):
    queryset = Order.objects.all()
    template = 'order_status.html'

    def get_object(self):
        token = self.kwargs.get('token', '')
        if not token:
            raise Http404()
        try:
            obj = Order.objects.verify_token(token)
        except BadSignature:
            raise Http404()
        return obj


class CancelOrderView(OrderSessionMixin, DeleteView):
    success_url = reverse_lazy('index')

    def get_context_data(self, **kwargs):
        """
        Sets url for user to return to previous view, depending on
        order status stored in session
        """
        context = super().get_context_data(**kwargs)
        order = self.request.session.get(self.key)
        back = 'shop:order' if order is None else 'shop:review'
        context['url'] = reverse(back)
        return context

    def delete(self, request, *args, **kwargs):
        """
        Soft deletes order and clears session cart and
        order information
        """
        cancel_order(
            instance=self.get_object(),
            cart=self.cart,
            key=self.key,
            session=request.session
        )
        messages.info(request, 'Your order has been canceled')
        return redirect(self.success_url)
