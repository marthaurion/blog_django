from rest_framework import serializers

from .models import Post
from comments.serializers import CommentSerializer


class PostDetailSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, required=False)
    category = serializers.StringRelatedField()
    tags = serializers.StringRelatedField(many=True)
    
    class Meta:
        model = Post
        
        fields = ('id', 'title', 'body_html', 'pub_date', 'category', 'tags', 'comments', )