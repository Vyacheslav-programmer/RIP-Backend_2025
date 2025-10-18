from rest_framework.exceptions import ValidationError
from rest_framework.permissions import BasePermission

from app.utils import identity_user


class IsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        user = identity_user(request)

        if user is None:
            err = ValidationError(detail="Учетные данные не были предоставлены")
            err.status_code = 401
            raise err

        return user.is_active


class IsBuyer(BasePermission):
    def has_permission(self, request, view):
        user = identity_user(request)

        if user is None:
            err = ValidationError(detail="Учетные данные не были предоставлены")
            err.status_code = 403
            raise err

        if user.is_superuser:
            err = ValidationError(detail="Недостаточно прав")
            err.status_code = 401
            raise err

        return user.is_active


class IsModerator(BasePermission):
    def has_permission(self, request, view):
        user = identity_user(request)

        if user is None:
            err = ValidationError(detail="Учетные данные не были предоставлены")
            err.status_code = 401
            raise err

        if not user.is_superuser:
            err = ValidationError(detail="Недостаточно прав")
            err.status_code = 403
            raise err

        return True
