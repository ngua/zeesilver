import re
import secrets
from django.db import models
from django.core import signing
from localflavor.us.models import USStateField, USZipCodeField
from common.models import BaseCustomer


class OrderManager(models.Manager):
    @staticmethod
    def generate_number():
        """
        Generates random hex number, converts it to an int, then to a string,
        then joins every 4th char with `-` to make a readable order number for
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

    def verify_token(self, token):
        value = signing.loads(token)
        number = value['number']
        return self.get(number=number)


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

    objects = OrderManager()

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = self.__class__.objects.generate_number()
        super().save(*args, **kwargs)

    def add_from_cart(self, cart):
        """
        Unpacks the serialized session cart and add each to the instance's
        listing set
        """
        self.listing_set.add(*cart)

    def soft_delete(self):
        """
        Preserves canceled orders
        """
        self.status = self.Status.CANCELED
        self.save()

    def summary(self):
        """
        Produces simple dictionary of attributes and labels for use in
        templates
        """
        return {
            'Name': self.name,
            'Address': self.address,
            'Phone': self.phone,
            'Email': self.email
        }

    def serialize(self):
        """
        Creates a simple representation of the order to be saved in the
        session
        """
        return {
            'number': self.number,
            'status': self.status
        }

    def token(self):
        """
        Creates token for URL
        """
        return signing.dumps({
            'number': self.number
        })

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
        return f'{self.number}, {self.name}, {self.email}'
