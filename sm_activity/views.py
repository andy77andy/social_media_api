from datetime import datetime
from django.db.models import Count
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from sm_activity.models import Profile, Comment, Post
from sm_activity.permissions import (
    IsOwnerOrIfAuthenticatedReadOnly,
    IsOwnerOrIfFollowerReadOnly,
)
from sm_activity.serializer import (
    ProfileSerializer,
    CommentSerializer,
    PostSerializer,
    ProfileDetailSerializer,
    ProfileFollowSerializer,
    PostDetailSerializer,
    LikePostSerializer,
    CommentPostSerializer,
)


class ProfileViewSet(
    viewsets.ModelViewSet,
):
    queryset = (
        Profile.objects.prefetch_related("posts", "follow_to")
        .annotate(posts_count=Count("posts"))
        .annotate(comments_count=Count("comments"))
    )
    serializer_class = ProfileSerializer
    permission_classes = (IsOwnerOrIfAuthenticatedReadOnly, IsAuthenticated)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ProfileDetailSerializer
        if self.action == "follow":
            return ProfileFollowSerializer
        return ProfileSerializer

    @action(
        methods=["GET"],
        detail=True,
        url_path="liked_posts",
        permission_classes=[IsOwnerOrIfFollowerReadOnly,],
    )
    def liked_posts(self, request, pk=None):
        print(self.get_permissions())
        profile_for_action = self.get_object()
        posts = profile_for_action.liked_posts.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=["GET"],
        detail=True,
        url_path="all_posts",
    )
    def all_posts(self, request, pk=None):

        profile_for_action = Profile.objects.get(pk=pk)
        posts = profile_for_action.posts.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=["POST"],
        detail=True,
        url_path="follow",
    )
    def follow(self, request, pk=None):
        user_profile = self.request.user.profile
        profile_for_action = Profile.objects.get(pk=pk)

        if (
            user_profile != profile_for_action
            and user_profile not in profile_for_action.followers.all()
        ):
            profile_for_action.followers.add(user_profile)
            return Response(
                {"detail": "Profile followed successfully."}, status=status.HTTP_200_OK
            )
        elif user_profile in profile_for_action.followers.all():
            profile_for_action.followers.remove(profile_for_action)
            return Response(
                {"detail": "you no longer follow this profile."},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"detail": "Unable to follow the profile."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def get_queryset(self):
        username = self.request.query_params.get("username")
        status_ = self.request.query_params.get("status")

        queryset = self.queryset

        if username:
            queryset = queryset.filter(username__icontains=username)

        if status_:
            queryset = queryset.filter(status__icontains=status_)

        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "username",
                type=OpenApiTypes.DATE,
                description="Filter by username (ex. ?Joe)",
            ),
            OpenApiParameter(
                "status",
                type=OpenApiTypes.DATE,
                description="Filter by status (ex. ?Active)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """
        this method is created for documentation, to use extend_schema
        for filtering
        """
        return super().list(self, request, *args, **kwargs)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.select_related(
        "author",
    ).prefetch_related("comments", "likes", "dislikes")
    permission_classes = (IsOwnerOrIfAuthenticatedReadOnly, IsAuthenticated)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user.profile)

    @action(
        methods=["POST"],
        detail=True,
        url_path="like",
        permission_classes=(IsAuthenticated,),
    )
    def like(self, request, pk=None) -> Response:
        post = self.get_object()
        user_profile = self.request.user.profile

        if (
            user_profile not in post.likes.all()
            and user_profile not in post.dislikes.all()
        ):
            post.likes.add(user_profile)
            return Response({"detail": "You like this post"}, status=status.HTTP_200_OK)
        elif user_profile in post.likes.all():
            post.likes.remove(user_profile)
            return Response(
                {"detail": "you didn't like this post anymore"},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"detail": "Unable to follow the profile."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(
        methods=["POST"],
        detail=True,
        url_path="dislike",
        permission_classes=(IsAuthenticated,),
    )
    def dislike(self, request, pk=None) -> Response:
        post = self.get_object()
        user_profile = self.request.user.profile

        if (
            user_profile not in post.likes.all()
            and user_profile not in post.dislikes.all()
        ):
            post.dislikes.add(user_profile)
            return Response(
                {"detail": "You dislike this post"}, status=status.HTTP_200_OK
            )
        elif user_profile in post.likes.all():
            post.dislikes.remove(user_profile)
            return Response(
                {"detail": "you didn't dislike this post anymore"},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"detail": "Unable to dislike the post"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def get_serializer_class(self):
        if self.action == "retrieve":
            return PostDetailSerializer
        if self.action in ("like", "dislike"):
            return LikePostSerializer
        if self.action == "comment":
            return CommentSerializer
        return PostSerializer

    @action(
        methods=["POST"],
        detail=True,
        url_path="comment",
        url_name="comment",
        permission_classes=(IsAuthenticated,),
    )
    def comment(self, request, pk=None) -> Response:
        post = self.get_object()
        user_profile = self.request.user.profile
        data = self.request.data

        serializer = CommentSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        comment = Comment.objects.create(
            post=post, owner=user_profile, body=serializer.data.get("body")
        )
        post.comments.add(comment)
        return Response({"detail": "Added your comment"}, status=status.HTTP_200_OK)

    def get_queryset(self):
        title = self.request.query_params.get("title")
        created_at = self.request.query_params.get("created_at")

        queryset = self.queryset

        if title:
            queryset = queryset.filter(title__icontains=title)

        if created_at:
            post_date = datetime.strptime(created_at, "%Y-%m-%d").date()
            queryset = queryset.filter(created_at=post_date)

        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "title",
                type=OpenApiTypes.DATE,
                description="Filter by title (ex. ?title=emmm..)",
            ),
            OpenApiParameter(
                "created_at",
                type=OpenApiTypes.DATE,
                description="Filter by creation day (ex. ?date=2020-10-10)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """
        this method is created for documentation, to use extend_schema
        for filtering
        """
        return super().list(self, request, *args, **kwargs)


class CommentViewSet(
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    queryset = Comment.objects.all()
    permission_classes = (IsOwnerOrIfAuthenticatedReadOnly,)
    serializer_class = CommentPostSerializer
