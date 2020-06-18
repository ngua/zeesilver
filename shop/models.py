import time
from django.db import models
from django.core import signing
from django.urls import reverse
from django.conf import settings
from django.db.models import signals
from django.dispatch import receiver
from localflavor.us.models import USStateField, USZipCodeField
from common.models import BaseCustomer
from .managers import OrderManager, PaymentManager


class Order(BaseCustomer):
    class Status(models.IntegerChoices):
        UNPAID = 1
        PAID = 2
        SHIPPED = 3
        CANCELED = 0

    # Hide the inherited `name` field from abstract base class
    name = None
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    street_address = models.CharField(max_length=127)
    city = models.CharField(max_length=32)
    state = USStateField()
    zip_code = USZipCodeField()
    # `null` and `blank` both required to avoid unique constraint violations
    number = models.CharField(
        max_length=16, blank=True, null=True, unique=True
    )
    status = models.PositiveIntegerField(
        choices=Status.choices, default=Status.UNPAID
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = OrderManager()

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = self.__class__.objects.generate_number()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('shop:status', kwargs={'token': self.token()})

    def add_from_cart(self, cart):
        """
        Unpacks the serialized session cart and add each item to the instance's
        listing set
        """
        self.listing_set.add(*cart)

    def soft_delete(self):
        """
        Preserves canceled orders
        """
        self.status = self.Status.CANCELED
        self.save()

    def finalize(self, session):
        self.status = self.Status.PAID
        self.save()
        del session[settings.CART_KEY]
        del session[settings.ORDER_KEY]

    def summary(self):
        """
        Produces dictionary of attributes and labels for use in template
        """
        return {
            'Name': self.name,
            'Address': self.address,
            'Phone': self.phone,
            'Email': self.email,
        }

    def serialize(self):
        """
        Creates representation of the order to be saved in the session
        """
        return {
            'number': self.number,
            'status': self.status,
            # Store when client was last active for timeout middleware
            'active': time.time(),
        }

    def token(self):
        """
        Creates token for URL
        """
        return signing.dumps({'number': self.number})

    def units(self):
        """
        Returns instance price in cents and string representation of currency
        """
        return str(self.total.currency), int(self.total.amount) * 100

    @property
    def paid(self):
        return hasattr(self, 'payment')

    @property
    def shipped(self):
        return hasattr(self, 'shipment')

    @property
    def total(self):
        return sum(listing.price for listing in self.listing_set.all())

    @property
    def name(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def address(self):
        return (
            f'{self.street_address}, {self.city}, {self.state}, '
            f'{self.zip_code}'
        )

    def __repr__(self):
        return f"Order('{self.first_name}', '{self.last_name}', {self.email})"

    def __str__(self):
        return f'#{self.number}'


class Payment(models.Model):
    square_payment_id = models.CharField(max_length=64)
    square_order_id = models.CharField(max_length=64)
    receipt_number = models.CharField(max_length=64)
    receipt_url = models.URLField()
    created = models.DateTimeField(auto_now_add=True)
    order = models.OneToOneField(Order, on_delete=models.CASCADE)

    objects = PaymentManager()

    def __repr__(self):
        return f"Payment('{self.square_order_id}')"

    def __str__(self):
        return f'#{self.square_order_id}'


class Provider(models.Model):
    name = models.CharField(max_length=255)

    def __repr__(self):
        return f"Provider('{self.name}')"

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'shipping provider'
        verbose_name_plural = 'shipping provider'


class Shipment(models.Model):
    provider = models.ForeignKey(
        Provider, on_delete=models.SET_NULL, null=True
    )
    created = models.DateTimeField(auto_now_add=True)
    tracking = models.CharField(max_length=127)
    order = models.OneToOneField(Order, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        # Check if instance is newly created. If so, set related order
        # instance status to shipped
        if not self.pk:
            self.order.status = Order.Status.SHIPPED
            self.order.save()
        super().save(*args, **kwargs)

    def __repr__(self):
        return f"Shipment('{self.tracking}')"

    def __str__(self):
        return f'#{self.tracking}'


@receiver(signals.post_save, sender=Shipment)
def notify_customer(sender, instance, created, **kwargs):
    """
    Sends notification to customer when new shipment is created
    """
    if created:
        # Avoid circular import with tasks module
        from .tasks import customer_tracking_notification

        # Call the task after short delay to ensure that transaction
        # has been committed
        customer_tracking_notification.apply_async(
            kwargs={'shipment_pk': instance.pk}, countdown=1
        )
