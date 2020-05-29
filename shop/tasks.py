from django.template import loader
from django.conf import settings
from django.core.mail.message import EmailMultiAlternatives
from celery.decorators import task
from html2text import html2text
from .models import Order


@task(name='customer_order_notification')
def customer_order_notification(order_pk, site_name):
    """
    Sends notification to customer after order is finalized
    """
    order = Order.objects.get(pk=order_pk)
    # Render HTML email template
    context = {
        'site_name': site_name,
        'order': order
    }
    body = loader.render_to_string('shop/order_email.html', context)
    # Convert HTML body to plaintext as fallback
    plain_text = html2text(body)

    from_email, to = settings.DEFAULT_FROM_EMAIL, order.email
    subject = f'Your Order at Zeesilver - {order.number}'

    email = EmailMultiAlternatives(
        subject=subject,
        body=plain_text,
        from_email=from_email,
        to=[to]
    )
    # Attach HTML version as alternative
    email.attach_alternative(body, 'text/html')
    email.send()
