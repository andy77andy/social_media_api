from django.test import TestCase

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


from sm_activity.models import Profile, Post
from sm_activity.serializer import (
    ProfileSerializer,
    ProfileDetailSerializer,
    ProfileFollowSerializer,
    PostDetailSerializer,
    PostSerializer,
)
from user.models import User

POSTS_URL = reverse("sm_activity:post-list")


def detail_url(post_id: int):
    return reverse("sm_activity:post-detail", args=[post_id])


def like_url(post_id: int):
    return reverse("sm_activity:post-like", args=[post_id])


def dislike_url(post_id: int):
    return reverse("sm_activity:post-dislike", args=[post_id])


def comment_url(post_id: int):
    return reverse("sm_activity:post-comment", args=[post_id])


def sample_post(**params):
    defaults = {
        "author": "",
        "title": "Test",
        "body": "hot_body",
    }
    defaults.update(params)

    return Post.objects.create(**defaults)


def sample_profile(**params):
    defaults = {
        "user": "",
        "username": "Test",
        "status": "Active",
        "bio": "Test",
    }
    defaults.update(params)

    return Profile.objects.create(**defaults)


class UnAuthProfileApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_forbidden_urls(self):
        user2 = get_user_model().objects.create_user("test@test2.com", "test3234")
        profile = sample_profile(
            user=user2,
            username="Test2",
        )
        sample_post(author=profile)

        response = self.client.get(POSTS_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PostApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "test1234"
            # , is_staff=True
        )

        self.client.force_authenticate(self.user)

    def test_update_post(self):
        profile_client = sample_profile(
            user=self.user,
            username="Test",
        )
        post = sample_post(author=profile_client)
        payload = {"title": "new_title", "body": "new_body"}
        response = self.client.put(detail_url(post.id), payload)
        serializer = PostDetailSerializer(post)
        post.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data["body"], payload["body"])

    def test_update_post_if_not_owner(self):
        user2 = get_user_model().objects.create_user("test@test2.com", "test3234")
        profile = sample_profile(
            user=user2,
            username="Test2",
        )
        profile_client = sample_profile(
            user=self.user,
            username="Test",
        )
        post = sample_post(author=profile)
        payload = {"title": "new_title", "body": "new_body"}
        response = self.client.put(detail_url(post.id), payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_post(self):
        profile_client = sample_profile(
            user=self.user,
            username="Test",
        )
        post = sample_post(author=profile_client)
        response = self.client.delete(detail_url(post.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_like_action(self):
        user2 = get_user_model().objects.create_user("test@test2.com", "test3234")
        profile = sample_profile(
            user=user2,
            username="Test2",
        )
        profile_client = sample_profile(
            user=self.user,
            username="Test",
        )
        post = sample_post(author=profile)

        response = self.client.post(like_url(post.id))
        serializer1 = PostDetailSerializer(post)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(profile_client.username, serializer1.data["likes"])

    def test_dislike_action(self):
        user2 = get_user_model().objects.create_user("test@test2.com", "test3234")
        profile = sample_profile(
            user=user2,
            username="Test2",
        )
        profile_client = sample_profile(
            user=self.user,
            username="Test",
        )
        post = sample_post(author=profile)

        response = self.client.post(dislike_url(post.id))
        serializer1 = PostDetailSerializer(post)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(profile_client.username, serializer1.data["dislikes"])

    def test_comment_action(self):
        user2 = get_user_model().objects.create_user("test@test2.com", "test3234")
        profile = sample_profile(
            user=user2,
            username="Test2",
        )
        post = sample_post(author=profile)
        profile_client = sample_profile(
            user=self.user,
            username="Test",
        )
        payload = {"body": "test"}

        response = self.client.post(comment_url(post.id), payload)
        serializer1 = PostSerializer(post)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, post.comments.count())
