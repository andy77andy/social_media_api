from rest_framework import routers

from sm_activity.views import (
    ProfileViewSet,
    PostViewSet,
    CommentViewSet,
)

router = routers.DefaultRouter()
router.register("profiles", ProfileViewSet)
router.register("posts", PostViewSet)
router.register("comments", CommentViewSet)

urlpatterns = router.urls

app_name = "sm_activity"
