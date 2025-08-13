from rest_framework.permissions import BasePermission, SAFE_METHODS

from .models import User


class IsAdmin(BasePermission):
    def has_permission(self, request, view):  # type: ignore[override]
        return bool(request.user and request.user.is_authenticated and getattr(request.user, "role", None) == User.Roles.ADMIN)


class IsSales(BasePermission):
    def has_permission(self, request, view):  # type: ignore[override]
        return bool(request.user and request.user.is_authenticated and getattr(request.user, "role", None) == User.Roles.SALES)


class IsAdminOrSales(BasePermission):
    def has_permission(self, request, view):  # type: ignore[override]
        return bool(request.user and request.user.is_authenticated and getattr(request.user, "role", None) in (User.Roles.ADMIN, User.Roles.SALES))


class IsCustomer(BasePermission):
    def has_permission(self, request, view):  # type: ignore[override]
        return bool(request.user and request.user.is_authenticated and getattr(request.user, "role", None) == User.Roles.CUSTOMER)

    def has_object_permission(self, request, view, obj):  # type: ignore[override]
        if request.method in SAFE_METHODS:
            return True
        owner = getattr(obj, "customer", None) or getattr(obj, "user", None)
        return owner == request.user