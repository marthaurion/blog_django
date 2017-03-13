from versatileimagefield.image_warmer import VersatileImageFieldWarmer
from precise_bbcode.bbcode import get_parser

from .models import Post, Media, Comment

# gets used if we need to populate the first image field for every model in the database
def populate_first_image():
    for post in Post.published.all():
        first = post.get_first_image()
        if first:
            post.first_image = first
            post.save()

def warm_all_media():
    media_img_warmer = VersatileImageFieldWarmer(
        instance_or_queryset=Media.objects.all(),
        rendition_key_set='scaled_image',
        image_attr='full_image'
    )
    num_created, failed_to_create = media_img_warmer.warm()
    
def convert_all_comments():
    parser = get_parser()
    for comment in Comment.objects.exclude(text__exact=''):
        comment.html_text = parser.render(comment.text)
        comment.save()