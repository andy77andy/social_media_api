import os
import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.text import slugify
from rest_framework.permissions import IsAuthenticated

from user.models import User


def image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    if isinstance(instance, Profile):
        filename = f"{slugify(instance.username)}-{uuid.uuid4()}{extension}"
        return os.path.join("uploads/profiles/", filename)
    elif isinstance(instance, Post):
        filename = f"{slugify(instance.title)}-{uuid.uuid4()}{extension}"
        return os.path.join("uploads/posts/", filename)


class Profile(models.Model):
    class StatusChoices(models.TextChoices):
        Active = "Active"
        Abandoned = "Long out of touch"
        Unknown = "Unknown"
    username = models.CharField(max_length=30, unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=30, choices=StatusChoices.choices)
    followers = models.ManyToManyField("self", related_name="follow_to", symmetrical=False, blank=True, )
    created_at = models.DateField(auto_now_add=True)
    image = models.ImageField(blank=True)
    bio = models.TextField(max_length=200)

    def __str__(self):
        return self.username

    class Meta:
        ordering = ("-created_at", "status",)


class Post(models.Model):
    author = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="posts")
    title = models.CharField(max_length=200)
    body = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(Profile, related_name="liked_posts")
    dislikes = models.ManyToManyField(Profile, related_name="disliked_posts")
    image = models.ImageField(blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.title}({self.author})"


class Comment(models.Model):
    post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)
    owner = models.ForeignKey(Profile, related_name="comments", on_delete=models.CASCADE)
    body = models.TextField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)
