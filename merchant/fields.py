from cryptography.fernet import Fernet
from django.db import models
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.encoding import force_bytes, force_str


class EncryptionField(models.Field):
    def __init__(self, *args, **kwargs):
        self.key = settings.FERNET_KEY
        if not self.key:
            raise ImproperlyConfigured(
                'Fernet key is not configured in settings module'
            )
        super().__init__(*args, **kwargs)

    @property
    def fernet(self):
        return Fernet(self.key)

    def get_internal_type(self):
        return 'BinaryField'

    def get_db_prep_save(self, value, connection):
        value = super().get_db_prep_save(value, connection)
        if value is not None:
            return connection.Database.Binary(
                self.fernet.encrypt(force_bytes(value))
            )

    def from_db_value(self, value, expression, connection):
        if value is not None:
            value = bytes(value)
            return self.to_python(force_str(self.fernet.decrypt(value)))
