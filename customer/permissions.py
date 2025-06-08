from rest_framework import permissions
from .models import UserRole

class IsSuperUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)

class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and 
                   request.user.is_staff and 
                   request.user.role and 
                   request.user.role.role == 'admin')

class IsManagerUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and 
                   request.user.is_staff and 
                   request.user.role and 
                   request.user.role.role == 'manager')

class IsCashierUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and 
                   request.user.is_staff and 
                   request.user.role and 
                   request.user.role.role == 'cashier')

class CanCreateStaff(permissions.BasePermission):
    """
    Permission to check if user can create staff members with specific roles
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_staff:
            return False
            
        # Superuser can create any role
        if request.user.is_superuser:
            return True
            
        # Regular users can't create staff
        if not request.user.role:
            return False
            
        # Check if user can create the requested role
        role_to_create = request.data.get('role')
        if not role_to_create:
            return False
            
        return role_to_create in UserRole.ROLE_HIERARCHY.get(request.user.role.role, [])
