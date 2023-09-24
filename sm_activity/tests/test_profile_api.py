from django.test import TestCase

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


from sm_activity.models import Profile
from sm_activity.serializer import ProfileSerializer, ProfileDetailSerializer, ProfileFollowSerializer

PROFILES_URL = reverse("sm_activity:profile-list")


def detail_url(profile_id: int):
    return reverse("sm_activity:profile-detail", args=[profile_id])


def like_url(profile_id: int):
    return reverse("sm_activity:profile-liked-posts", args=[profile_id])


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

    def test_forbidden(self):
        user2 = get_user_model().objects.create_user(
            "test@test2.com", "test3234"
        )
        sample_profile(
            user=user2,
            username="Test2",
        )

        response = self.client.get(PROFILES_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ProfileApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com", "test1234"
        )

        self.client.force_authenticate(self.user)

    def test_follow_and_permission(self):
        user2 = get_user_model().objects.create_user(
            "test@test2.com", "test3234"
        )
        profile_1 = sample_profile(
            user=self.user,
            username="Test1",
        )
        profile_2 = sample_profile(
            user=user2,
            username="Test2",
        )

        profile_2.followers.add(profile_1)
        serializer1 = ProfileDetailSerializer(profile_2)
        serializer2 = ProfileFollowSerializer(profile_1)
        response = self.client.get(detail_url(profile_id=2))
        response2 = self.client.get(like_url(profile_id=2))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(serializer2.data, serializer1.data["followers"])
        self.assertEqual(response2.status_code, status.HTTP_200_OK)

    def test_update_profile_by_owner(self):
        profile_1 = sample_profile(
            user=self.user,
            username="Test1",
        )
        payload = {
            "bio": "Test2",
        }
        serializer1 = ProfileDetailSerializer(profile_1)
        url = detail_url(profile_1.id)
        response = self.client.patch(url, payload, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(serializer1.data["bio"], payload["bio"])

    def test_update_profile_forbidden(self):
        user2 = get_user_model().objects.create_user(
            "test@test2.com", "test3234"
        )
        profile_1 = sample_profile(
            user=user2,
            username="Test1",
        )
        payload = {
            "bio": "Test2",
        }
        url = detail_url(profile_1.id)
        response = self.client.patch(url, payload, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_filtering_profiles(self):
        user2 = get_user_model().objects.create_user(
            "test@test2.com", "test3234"
        )
        user3 = get_user_model().objects.create_user(
            "test@test3.com", "test3334"
        )
        profile_1 = sample_profile(
            user=self.user,
            username="Test1",
            status="Abandoned"
        )
        profile_2 = sample_profile(
            user=user2,
            username="Test2",
            created_at="2023-08-18",
        )
        profile_3 = sample_profile(
            user=user3,
            username="Test3",
            status="None"
        )

        response = self.client.get(PROFILES_URL, {"username": "Test1"}).json()
        response2 = self.client.get(PROFILES_URL, {"status": "Active"}).json()
        serializer1 = ProfileSerializer(profile_1, many=False)
        serializer2 = ProfileSerializer(profile_2, many=False)
        serializer3 = ProfileSerializer(profile_3, many=False)

        self.assertEqual(serializer1.data["username"], response[0]["username"] )
        self.assertIn(serializer2.data["username"], response2[0]["username"])
        self.assertNotIn(serializer3.data, response)

    def test_forbidden_urls(self):
        user2 = get_user_model().objects.create_user(
            "test@test2.com", "test3234"
        )
        sample_profile(
            user=self.user,
            username="Test1",
        )
        sample_profile(
            user=user2,
            username="Test2",
        )

        response = self.client.get(like_url(profile_id=2))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
