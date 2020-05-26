from django.conf import settings


def square_connect_request(**kwargs):
    """
    Generic utility to construct requests to Square Connect OAuth endpoint,
    takes arbitrary number of kwargs to populate dictionary with parameters
    for request
    """
    body = {
        'client_id': settings.SQUARE_APPLICATION_ID,
        'client_secret': settings.SQUARE_APPLICATION_SECRET,
    }
    if kwargs:
        body.update(kwargs)
    return body
