from rest_framework.permissions import BasePermission
from .models import UserProfile, Role


def _role(user) -> str:
    try:
        return user.userprofile.role
    except UserProfile.DoesNotExist:
        return Role.CUSTOMER


class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and _role(request.user) == Role.CUSTOMER


class IsOwner(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and _role(request.user) == Role.OWNER


class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (
            request.user.is_staff or _role(request.user) == Role.ADMIN
        )
