from versatileimagefield.image_warmer import VersatileImageFieldWarmer
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from .models import Post, Media

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
        

class PostPaginator(Paginator):
    def validate_number(self, number):  # overwrite validation so it allows empty pages all the time
        try:
            number = int(number)
        except (TypeError, ValueError):
            raise PageNotAnInteger('That page number is not an integer')
        if number < 1:
            raise EmptyPage('That page number is less than 1')
        if not self.allow_empty_first_page:
            if number > self.num_pages:
                raise EmptyPage('That page contains no results')
        return number