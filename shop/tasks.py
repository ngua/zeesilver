from celery.decorators import task
from common.utils import get_site_name
from .models import Order, Shipment
from .utils import mail_customer


@task(name='customer_order_notification')
def customer_order_notification(order_pk):
    """
    Sends notification to customer after order is finalized
    """
    order = Order.objects.get(pk=order_pk)
    # Create template context
    context = {'order': order, 'site_name': get_site_name()}
    subject = f'Your Order at Zeesilver - {order.number}'
    to = order.email
    template = 'shop/order_email.html'
    mail_customer(template, context, subject, to)


@task(name='customer_tracking_notification')
def customer_tracking_notification(shipment_pk):
    """
    Sends tracking number to customer after Shipping object is created
    """
    shipment = Shipment.objects.get(pk=shipment_pk)
    # Create template context
    context = {'shipment': shipment, 'site_name': get_site_name()}
    subject = f'Tracking information for #{shipment.order}'
    to = shipment.order.email
    template = 'shop/order_tracking_email.html'
    mail_customer(template, context, subject, to)
