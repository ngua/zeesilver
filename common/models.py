from django.db import models
from django.contrib.auth.models import AbstractUser
from solo.models import SingletonModel


class User(AbstractUser):
    pass


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
