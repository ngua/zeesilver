from django.conf import settings
from django.template import loader
from django.core.mail.message import EmailMultiAlternatives
from html2text import html2text


def mail_customer(template, context, subject, to, from_email=None):
    """
    Generic utility to send email notifications to customers
    """
    if from_email is None:
        from_email = settings.DEFAULT_FROM_EMAIL

    body = loader.render_to_string(template, context)
    # Convert HTML body to plaintext as fallback
    plain_text = html2text(body)
    email = EmailMultiAlternatives(
        subject=subject,
        body=plain_text,
        from_email=from_email,
        to=[to]
    )
    # Attach HTML version as alternative
    email.attach_alternative(body, 'text/html')
    email.send()


def cancel_order(instance, cart, key, session):
    """
    Calls soft delete method of Order instance and clears session cart
    """
    cart.clear()
    instance.soft_delete()
    del session[key]
