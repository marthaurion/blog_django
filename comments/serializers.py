from rest_framework import serializers
from .models import Comment, Commenter

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