from celery.decorators import task
from celery.utils.log import get_task_logger
from .models import Comment

logger = get_task_logger(__name__)

@task(name="send_email_notification")
def send_email(comment_id, info_dict):
    comment_set = Comment.objects.filter(pk=comment_id)
    if comment_set:
        comment = comment_set[0]
        logger.info('Sending email notifications for comment %s', comment_id)
        comment.send_notifications(info_dict)