from django.db import models
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from django.conf import settings
from solo.models import SingletonModel
from .fields import EncryptionField


class SquareConfig(SingletonModel):
    """
    Singleton model to hold Square Payment OAuth2 configuration. The single
    instance will be created automatically, so blank and null fields must be
    allowed
    There is only one merchant user, so a singleton model would be appropriate
    to hold Square Connect configuration details
    """
    access_token = EncryptionField(null=True)
    refresh_token = EncryptionField(null=True)
    expires = models.DateTimeField(null=True)
    created = models.DateTimeField(null=True)
    active = models.BooleanField(default=False)
    obtained_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )

    def update(self, access_token, refresh_token, expires, user):
        """
        Update the fields directly through model , rather than filtering
        through manager and updating
        """
        try:
            self.expires = parse_datetime(expires)
        except ValueError:
            pass
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.user = user
        self.active = True
        self.created = timezone.now()
        self.save()

    @classmethod
    def reset(cls):
        """
        Delete existing singleton instance in order to erase existing OAuth
        configuration
        """
        cls.get_solo().delete()

    def __str__(self):
        return self.__class__.__name__

    class Meta:
        verbose_name = 'Square Payment Configuration'
        permissions = [
            (
                'obtain_tokens',
                'Can request or revoke tokens from Square OAuth endpoint'
            )
        ]
