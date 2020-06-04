import io
import json
import weasyprint
from uuid import uuid4
from collections import OrderedDict
from django.conf import settings
from django.contrib import messages
from django.template import loader
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.http import Http404, JsonResponse, FileResponse
from django.core.signing import BadSignature
from django.views.generic import (
    View, CreateView, DetailView, DeleteView, UpdateView
)
from django.views.generic.base import ContextMixin
from django.views.generic.detail import SingleObjectMixin
from django.contrib.sites.shortcuts import get_current_site
from square.client import Client
from common.tasks import notify_admins
from cart.cart import Cart
from .models import Order, Payment
from .forms import OrderForm
from .utils import cancel_order
from .tasks import customer_order_notification


class ProgressMixin(ContextMixin):
    """
    Adds order steps and current progress to context for display in template
    """
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


class OrderMixin(ProgressMixin, View):
    """
    Instantiates session cart for order views
    """
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


class SessionMixin(SingleObjectMixin, OrderMixin):
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


class ReviewOrderView(SessionMixin, DetailView):
    pass


class UpdateOrderView(SessionMixin, UpdateView):
    form_class = OrderForm
    success_url = reverse_lazy('shop:review')
    template_name = 'shop/order_update_form.html'

    def get_context_data(self, **kwargs):
        """
        Sets the current view for CSS styling in progress bar and adds action
        to generic form in template
        """
        context = super().get_context_data(**kwargs)
        # Change the current step back to create view
        context.update({
            'current': 'OrderCreateView',
            'action': reverse('shop:update')
        })
        return context


class PaymentView(SessionMixin, DetailView):
    template_name = 'shop/order_pay.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add necessary context to include in json_script tags
        context.update({
            'square_application_id': settings.SQUARE_APPLICATION_ID,
            'payment_url': reverse('shop:charge'),
            'amount': self.object.total,
            'square_payment_library': settings.SQUARE_PAYMENT_LIBRARY
        })
        return context


class ChargeView(SessionMixin):  # pragma: no cover
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        client = Client(
            access_token=settings.SQUARE_ACCESS_TOKEN,
            environment=settings.SQUARE_ENVIRONMENT
        )
        data = json.loads(request.body)
        nonce = data.get('nonce')
        if nonce is None:
            return self.charge_invalid()

        currency, amount = self.object.units()
        idempotency_key = str(uuid4())
        body = {
            'source_id': nonce,
            'idempotency_key': idempotency_key,
            'amount_money': {
                'currency': currency,
                'amount': amount
            }
        }
        result = client.payments.create_payment(body)
        if result.is_success():
            return self.charge_valid(result)
        else:
            return self.charge_invalid()

    def charge_valid(self, result):
        Payment.objects.from_response(result, self.object)
        self.object.finalize(self.request.session)
        customer_order_notification.delay(
            order_pk=self.object.pk,
            site_name=str(get_current_site(self.request))
        )
        notify_admins.delay(
            subject='New Order at zeesilver.com',
            body=loader.render_to_string(
                'shop/order_admin_email.html',
                {'order': self.object}
            )
        )
        return JsonResponse({'url': self.object.get_absolute_url()})

    def charge_invalid(self):
        cancel_order(
            instance=self.object,
            cart=self.cart,
            key=self.key,
            session=self.request.session
        )
        return JsonResponse({'url': reverse('index')})


class StatusMixin:
    queryset = Order.objects.all()

    """
    Retrieves and decodes token from url kwarg
    """
    def get_object(self):
        token = self.kwargs.get('token')
        try:
            obj = Order.objects.verify_token(token)
            return obj
        except BadSignature:
            raise Http404()


class OrderStatusView(StatusMixin, DetailView):
    template_name = 'shop/order_status.html'


class OrderInvoiceView(StatusMixin, DetailView):
    template_name = 'shop/order_invoice.html'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(**kwargs)
        buffer = io.BytesIO()
        html = loader.render_to_string(self.template_name, context)
        # TODO remove hard-coded css path
        stylesheet = weasyprint.CSS('/app/static/styles/css/app.css')
        weasyprint.HTML(string=html).write_pdf(
            buffer, stylesheets=[stylesheet]
        )
        buffer.seek(0)
        return FileResponse(buffer, filename='invoice.pdf')


class OrderResendEmailView(StatusMixin, DetailView):
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        customer_order_notification.delay(
            order_pk=self.object.pk,
            site_name=str(get_current_site(self.request))
        )
        return JsonResponse({
            'message': 'Order confirmation email sent!'
        })


class CancelOrderView(SessionMixin, DeleteView):
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
