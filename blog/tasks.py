from celery.decorators import task
from .models import Comment

@task(name="send_email_notification")
def send_email(comment_id, info_dict):
    comment_set = Comment.objects.filter(pk=comment_id)
    if comment_set:
        comment_set[0].send_notifications(info_dict)