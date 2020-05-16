from django.db import models
from django.core.validators import RegexValidator


class Contact(models.Model):

    class Subject(models.TextChoices):
        SALES = 'SALES'
        RETURNS = 'RETURNS'
        CUSTOM = 'CUSTOM'
        OTHER = 'OTHER'

    phone_validator = RegexValidator(
        r'^\(?[2-9]\d{2}\)?\s?\d{3}(?:\-|\s)?\d{4}$',
        message='Please enter a valid US phone number, including area code',
    )

    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(
        max_length=14, validators=[phone_validator], blank=True
    )
    subject = models.CharField(
        max_length=8, choices=Subject.choices, default=Subject.SALES
    )
    message = models.TextField()
    date = models.DateField(auto_now_add=True)

    def __repr__(self):
        return f"Contact('{self.name}, {self.email}')"

    def __str__(self):
        return f'{self.name}: ({self.email}), {self.date.strftime("%D %H:%M")}'
