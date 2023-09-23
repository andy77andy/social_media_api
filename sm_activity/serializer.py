from rest_framework import serializers, status
from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from sm_activity.models import Profile, Comment, Post


class CommentSerializer(serializers.ModelSerializer):
    owner = serializers.CharField(source="owner.username", read_only=True)

    class Meta:
        model = Comment
        fields = ("id", "body", "created_at", "owner")


class ProfileSerializer(serializers.ModelSerializer):
    followers = serializers.IntegerField(source="followers.count", read_only=True, )
    follow_to = serializers.IntegerField(source="follow_to.count", read_only=True, )
    comments_count = serializers.IntegerField(read_only=True)
    posts_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Profile
        fields = ("id", "username", "user", "status", "image", "bio", "followers", "follow_to", "posts_count", "comments_count", )


class ProfileFollowSerializer(serializers.ModelSerializer):
    username = serializers.CharField(read_only=True)
    image = serializers.ImageField(read_only=True)

    class Meta:
        model = Profile
        fields = ("username", "image",)


class ProfileDetailSerializer(serializers.ModelSerializer):
    followers = ProfileFollowSerializer(many=True, read_only=True)
    follow_to = ProfileFollowSerializer(many=True, read_only=True)
    posts = serializers.SerializerMethodField()

    def get_posts(self, obj) -> list:
        return [post.title for post in obj.posts.all()] 

    class Meta:
        model = Profile
        fields = ("id", "username", "user", "status", "image", "followers", "follow_to", "posts", "bio")


class PostSerializer(serializers.ModelSerializer):
    comments = serializers.IntegerField(source="comments.count", read_only=True)
    author = serializers.CharField(source="author.username", read_only=True)
    likes = serializers.IntegerField(source="likes.count", read_only=True)
    dislikes = serializers.IntegerField(source="dislikes.count", read_only=True)

    class Meta:
        model = Post
        fields = ("id", "title", "body", "author", "created_at", "comments", "image", "likes", "dislikes",)


class CommentPostSerializer(serializers.ModelSerializer):
    owner = serializers.CharField(source="owner.username", read_only=True)

    class Meta:
        model = Comment
        fields = ("body", "owner", "created_at", )


class LikePostSerializer(serializers.ModelSerializer):
    owner = serializers.CharField(source="owner.username", read_only=True)

    class Meta:
        model = Comment
        fields = ("title", "owner", "created_at",)


class PostDetailSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source="author.username", read_only=True)
    comments = CommentPostSerializer(many=True, read_only=True)
    likes = serializers.SerializerMethodField()
    dislikes = serializers.SerializerMethodField()

    def get_likes(self, obj) -> list:
        return [likes.username for likes in obj.likes.all()]

    def get_dislikes(self, obj) -> list:
        return [dislikes.username for dislikes in obj.dislikes.all()]

    class Meta:
        model = Post
        fields = ("id", "title", "body", "author", "created_at", "comments", "likes", "dislikes", )

