from django.test import TestCase

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


from sm_activity.models import Profile, Post, Comment


def comment_url(post_id: int):
    return reverse("sm_activity:post-comment", args=[post_id])


def detail_url(comment_id: int):
    return reverse("sm_activity:comment-detail", args=[comment_id])


def sample_profile(**params):
    defaults = {
        "user": "",
        "username": "Test",
        "status": "Active",
        "bio": "Test",
    }
    defaults.update(params)

    return Profile.objects.create(**defaults)


def sample_post(**params):
    defaults = {
        "author": "",
        "title": "Test",
        "body": "hot_body",
    }
    defaults.update(params)

    return Post.objects.create(**defaults)


class CommentApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user("test@test.com", "test1234")
        self.client.force_authenticate(self.user)

    def test_update_comment(self):
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
        payload = {"body": "it's so dope!"}
        payload_1 = {"body": "what a mess!!"}

        response = self.client.post(comment_url(post.id), payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        payload_1 = {"body": "what a mess!!"}
        comment = Comment.objects.get(id=1)
        response_1 = self.client.put(detail_url(1), payload_1)
        comment.refresh_from_db()
        self.assertEqual(response_1.status_code, status.HTTP_200_OK)
        self.assertEqual(comment.body, payload_1["body"])

    def test_delete_comment(self):
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
        payload = {"body": "it's so dope!"}

        self.client.post(comment_url(post.id), payload)
        response_1 = self.client.delete(detail_url(1))
        self.assertEqual(response_1.status_code, status.HTTP_204_NO_CONTENT)
