from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    is_merchant = models.BooleanField(default=False)


class Merchant(models.Model):
    user = models.OneToOneField('User', on_delete=models.CASCADE)
    square_token = models.CharField(max_length=255, blank=True)
