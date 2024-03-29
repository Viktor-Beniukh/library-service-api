from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrIfAllowAnyReadOnly(BasePermission):
    def has_permission(self, request, view) -> bool:
        return bool(
            request.method in SAFE_METHODS
            or (request.user and request.user.is_staff)
        )


class IsAdminOrIfAuthenticatedReadOnly(BasePermission):
    def has_permission(self, request, view) -> bool:
        return bool(
            (
                request.method in SAFE_METHODS
                and request.user
                and request.user.is_authenticated
            )
            or (request.user and request.user.is_staff)
        )
