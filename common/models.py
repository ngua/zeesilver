from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from solo.models import SingletonModel


class User(AbstractUser):
    pass


class BaseCustomer(models.Model):
    """
    Base class for creating customer/contact models
    """
    phone_validator = RegexValidator(
        r'^\(?[2-9]\d{2}\)?\s?\d{3}(?:\-|\s)?\d{4}$',
        message='Please enter a valid US phone number, including area code',
    )

    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(
        max_length=14, validators=[phone_validator], blank=True
    )

    class Meta:
        abstract = True


class Carousel(SingletonModel):
    """
    Singleton model for carousel in index view. Can be edited from admin
    interface using Slide inline defined in admin module
    """
    def __str__(self):
        return 'Homepage Carousel'

    class Meta:
        verbose_name = 'carousel'


def slide_upload_path(instance, filename):
    return f'slides/{filename}'


class Slide(models.Model):
    """
    Individual slides that compose Carousel model above
    """
    caption = models.CharField(max_length=255)
    picture = models.ImageField(upload_to=slide_upload_path)
    carousel = models.ForeignKey(Carousel, on_delete=models.CASCADE)

    def __repr__(self):
        return f"Slide('{self.caption}', '{self.picture}')"

    def __str__(self):
        return self.caption
