import re
import secrets
from django.db import models
from localflavor.us.models import USStateField, USZipCodeField
from common.models import BaseCustomer


class OrderManager(models.Manager):
    @staticmethod
    def generate_number():
        """
        Generate random order number in hex, convert to int, then to string,
        and join every 4th char with `-` to make a readable order number for
        customers

        Example: `6769-2583-4952`

        NOTE Depending on the hex value returned by secrets, the int may be
        12 digits or 8 (much higher probability of the former). Loop ensures
        consistent length
        """
        while True:
            number = '-'.join(re.findall(
                r'\d{4}', str(int(secrets.token_hex(6), 16))
            ))
            if len(number) == 14:
                return number


class Order(BaseCustomer):

    class Status(models.IntegerChoices):
        UNPAID = 1
        PAID = 2
        SHIPPED = 3
        CANCELLED = 0

    # Hide the inherited `name` field from abstract base class
    name = None
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    address = models.CharField(max_length=16)
    city = models.CharField(max_length=32)
    state = USStateField()
    zip_code = USZipCodeField()
    number = models.CharField(max_length=16, blank=True)
    status = models.PositiveIntegerField(
        choices=Status.choices, default=Status.UNPAID
    )
    created = models.DateTimeField(auto_now_add=True)

    objects = OrderManager()

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = self.generate_number()
        super().save(*args, **kwargs)

    def add_from_cart(self, cart):
        self.listing_set.add(*cart)

    @property
    def total(self):
        return sum(listing.price for listing in self.listing_set.all())
