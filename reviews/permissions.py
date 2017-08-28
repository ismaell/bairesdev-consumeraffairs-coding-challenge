from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    """
    Allow access only to review owner and staff
    """
    def has_object_permission(self, req, view, obj):
        return (obj.reviewer == req.user) or req.user.is_staff
