from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrIfAuthenticatedReadOnly(BasePermission):
    def has_permission(self, request, view):
        return bool(
            (
                request.method in SAFE_METHODS
                and request.user
                and request.user.is_authenticated
            )
            or (request.user and request.user.is_staff)
        )


class IsOwnerOrIfAuthenticatedReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if (
            request.method in SAFE_METHODS
            and request.user
            and request.user.is_authenticated
        ):
            return True
        if hasattr(obj, "author"):
            return obj.author.user == request.user

        if hasattr(obj, "owner"):
            return obj.owner.user == request.user

        if hasattr(obj, "user"):
            return obj.user == request.user

        return False


class IsOwnerOrIfFollowerReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if (
            request.method in SAFE_METHODS
            and request.user
            and request.user.is_authenticated
            and request.user.profile
            and request.user.profile in obj.followers.all()
        ):
            return True

        if hasattr(obj, "user"):
            return obj.user == request.user

        return False

