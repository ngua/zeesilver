from django.db import models
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from django.conf import settings
from solo.models import SingletonModel
from .fields import EncryptionField


class SquareConfig(SingletonModel):
    """
    Singleton model to hold Square Connect OAuth2 configuration. There is only
    one merchant user, so a single instance is appropriate.  As it's created
    automatically if it doesn't exist, null fields must be allowed. The
    instance can only be modified or deleted through the views defined in the
    present app. Both tokens are encrypted and stored as binary data
    """
    access_token = EncryptionField(null=True)
    refresh_token = EncryptionField(null=True)
    expires = models.DateTimeField(null=True)
    created = models.DateTimeField(null=True)
    # Flag if the instance is usable
    active = models.BooleanField(default=False)
    obtained_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )

    def update(self, user, body):
        """
        Update the fields directly through model , rather than filtering
        through manager and updating
        Takes `body` attribute of Square client instnace
        """
        try:
            self.expires = parse_datetime(body.get('expires_at', ''))
        except ValueError:
            pass  # TODO derive the expiration based on creation date
        self.access_token = body.get('access_token', '')
        self.refresh_token = body.get('refresh_token', '')
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
