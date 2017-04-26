from precise_bbcode.bbcode import get_parser

from .models import Comment

def convert_all_comments():
    parser = get_parser()
    for comment in Comment.objects.exclude(text__exact=''):
        comment.html_text = parser.render(comment.text)
        comment.save()