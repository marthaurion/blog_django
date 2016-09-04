from django.contrib.syndication.views import Feed

from .models import Post

class LatestEntriesFeed(Feed):
    title = "Marth's Anime Blog Feed"
    link = "/blog/"
    description = "Updates with new blog posts."

    def items(self):
        return Post.published.order_by('-pub_date')[:5]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.body_html
        
    def item_pubdate(self, item):
        return item.pub_date