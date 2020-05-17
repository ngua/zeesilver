from celery.decorators import task
from celery.utils.log import get_task_logger
from .models import Listing


logger = get_task_logger(__name__)


@task(name='update_search_task')
def update_search_task(pk):
    """
    Updates a Listing instance's search vector field following
    db saves. Not strictly necessary at this stage to offload it
    to a Celery task, but will scale better as db rows increase
    """
    instance = Listing.objects.query_summary().get(pk=pk)
    instance.search_vector = instance.summary
    instance.save(update_fields=['search_vector'])
