from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class SpacesStaticStorage(S3Boto3Storage):
    location = settings.STATICFILES_LOCATION


class SpacesMediaStorage(S3Boto3Storage):
    location = settings.MEDIAFILES_LOCATION
