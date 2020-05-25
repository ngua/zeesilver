# from celery.decorators import periodic_task
# from celery.schedules import crontab
# from celery.utils.log import get_logger
# from square.client import Client


# logger = get_logger(__name__)


# @periodic_task(run_every=crontab(minute=0, hour=0))
# def refresh_square_oauth():
#     square_config = SquareConfig.get_solo()
#     if not square_config.active:
#         logger.info('No active Square Connect tokens, skipping task...')
#         return

#     client = Client(
#         access_token=settings.SQUARE_ACCESS_TOKEN,
#         environment=settings.SQUARE_ENVIRONMENT
#     )
#     oauth_api = client.o_auth
