from collections import OrderedDict
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    View, CreateView, DetailView, DeleteView, UpdateView
)
from django.views.generic.base import ContextMixin
from django.http import Http404
from cart.cart import Cart
from .models import Order
from .forms import OrderForm


class OrderMixin(ContextMixin, View):
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
            return redirect(reverse('index'))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            # Add checkout steps to context for users to see progress
            'steps': OrderedDict([
                ('Shipping Information', 'OrderCreateView'),
                ('Review Your Order', 'ReviewOrderView'),
                ('Payment', 'PaymentView')
            ]),
            # Get current view name to style with CSS in template
            'current': self.__class__.__name__
        })
        return context


class OrderSessionMixin(OrderMixin):
    """
    Retrieves serialized order from session
    """
    queryset = Order.objects.all()

    def get_object(self):
        order = self.request.session.get(self.key)
        if order is None:
            raise Http404('No Order Found')
        number = order['number']
        return self.queryset.get(number=number)


class OrderCreateView(OrderMixin, CreateView):
    form_class = OrderForm
    success_url = reverse_lazy('shop:review')

    def get_context_data(self, **kwargs):
        """
        Adds view name for form action (form is generic)
        """
        context = super().get_context_data(**kwargs)
        context['action'] = reverse('shop:order')
        return context

    def form_valid(self, form):
        """
        Deserializes the session cart and add items to order listing set
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

    def get_context_data(self, **kwargs):
        """
        Sets the current view for CSS styling in order progress bar and adds
        action to generic form in template
        """
        context = super().get_context_data(**kwargs)
        context.update({
            'current': 'OrderCreateView',
            'action': reverse('shop:update')
        })
        return context


class PaymentView(OrderSessionMixin):
    pass


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
        Soft deletes order and clears session cart
        """
        self.cart.clear()
        instance = self.get_object()
        instance.soft_delete()
        messages.info(request, 'Your order has been canceled')
        return redirect(self.success_url)
