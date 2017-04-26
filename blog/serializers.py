from rest_framework import serializers
from .models import Post, Comment, Commenter


class CommenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Commenter
        fields = ('id', 'username', 'email', 'website')
        

class CommentSerializer(serializers.ModelSerializer):
    parent = serializers.PrimaryKeyRelatedField(read_only=True, required=False)
    author = CommenterSerializer()
    
    class Meta:
        model = Comment
        
        fields = ('id', 'author', 'parent', 'html_text', 'get_absolute_url')


class PostSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, required=False)
    category = serializers.StringRelatedField()
    tags = serializers.StringRelatedField(many=True)
    
    class Meta:
        model = Post
        
        fields = ('id', 'title', 'body_html', 'pub_date', 'category', 'tags', 'comments', )