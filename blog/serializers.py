from rest_framework import serializers
from .models import Post, Category, Comment


class PostSerializer(serializers.ModelSerializer):
    category = serializers.ReadOnlyField(source='category.name')
    author = serializers.ReadOnlyField(source='author.name')
    image = serializers.ImageField(max_length=None, allow_empty_file=False, use_url=True)
    class Meta:
        model = Post
        fields = (
            'id',
            'category',
            'author',
            'title',
            'slug',
            'content',
            'image',
            'get_thumbnail',
            'pub_date'
       )

class CategorySerializer(serializers.ModelSerializer):
    posts = PostSerializer(many=True)
    class Meta:
        model = Category
        fields = ['name', 'slug', 'posts']

class CommentSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    post_title = serializers.SerializerMethodField()

    def get_user_name(self, comment):
        return comment.user.name

    def get_post_title(self, comment):
        return comment.post.title

    class Meta:
        model = Comment
        fields = ['id', 'user_name', 'post', 'post_title', 'body', 'created_on']

    def __init__(self, *args, **kwargs):
        # Retrieve the post instance from the context
        post = kwargs.pop('post', None)
        super().__init__(*args, **kwargs)

        # Restrict the queryset for the 'post' field to the provided post instance
        if post is not None:
            self.fields['post'].queryset = Post.objects.filter(pk=post.pk)
