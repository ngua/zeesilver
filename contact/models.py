from django.db import models
from common.models import BaseCustomer


class Contact(BaseCustomer):

    class Subject(models.TextChoices):
        SALES = 'SALES'
        RETURNS = 'RETURNS'
        CUSTOM = 'CUSTOM'
        OTHER = 'OTHER'

    subject = models.CharField(
        max_length=8, choices=Subject.choices, default=Subject.SALES
    )
    message = models.TextField()
    date = models.DateField(auto_now_add=True)

    def __repr__(self):
        return f"Contact('{self.name}, {self.email}')"

    def __str__(self):
        return f'{self.name}: ({self.email}), {self.date.strftime("%D %H:%M")}'
