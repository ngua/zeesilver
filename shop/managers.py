import re
import secrets
from django.db import models
from django.core import signing


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
        """
        Unsigns token and returns Order instance with matching number
        """
        value = signing.loads(token)
        number = value['number']
        return self.get(number=number)


class PaymentManager(models.Manager):
    def from_response(self, response, order):
        """
        Creates a new Payment instance from response object returned from
        Square Connect payment endpoint. Takes Square Client response object
        and Order instance as params
        """
        payment = response.body.get('payment', {})
        params = {
            'square_payment_id': payment.get('id', ''),
            'square_order_id': payment.get('order_id', ''),
            'status': payment.get('status', ''),
            'order': order
        }
        return self.create(**params)
