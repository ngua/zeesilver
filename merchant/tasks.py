from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from celery.decorators import periodic_task, task
from celery.schedules import crontab
from celery.utils.log import get_logger
from square.client import Client
from .utils import square_connect_request
from .models import SquareConfig


logger = get_logger(__name__)


@periodic_task(run_every=crontab(minute=0, hour=0))
def refresh_square_oauth():
    """
    Task to periodically send refresh request to Square Connect endpoint, if
    current tokens exist
    """
    square_config = SquareConfig.get_solo()
    if not square_config.active:
        logger.info('No active Square Connect tokens, skipping task...')
        return

    client = Client(
        access_token=settings.SQUARE_ACCESS_TOKEN,
        environment=settings.SQUARE_ENVIRONMENT
    )
    oauth_api = client.o_auth

    body = square_connect_request(
        grant_type='refresh_token',
        refresh_token=square_config.refresh_token
    )
    result = oauth_api.obtain_token(body)
    if result.is_success():
        square_config.update(body=result.body)
        logger.info('Square OAuth renewal succeeded')
    # Explicitly check for `error` attribute
    elif result.is_error():
        logger.error(
            f'Square renewal failed: {result.errors} ({result.type})'
        )


@periodic_task(run_every=crontab(minute=0, hour=0))
def mark_inactive():
    """
    Task to ensure that a SquareConfig instance with expired tokens is marked
    as inactive so it can't be used to try to process payments any longer.
    Useful as a backup if token refresh fails for some reason

    NOTE Using Celery's `eta` feature would be an option here (if it's called
    upon saving SquareConfig instance), but task ID would have to be stored
    in order to cancel it upon token refresh
    """
    square_config = SquareConfig.get_solo()
    if not square_config.active:
        logger.info('No active Square Connect tokens, skipping task...')
        return
    if square_config.expires - timezone.now() < timedelta(days=1):
        square_config.active = False
        square_config.save()
