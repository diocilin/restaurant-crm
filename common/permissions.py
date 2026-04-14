from rest_framework.permissions import BasePermission

class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        return request.user and request.user.is_staff

class IsStoreStaff(BasePermission):
    """店员只能访问本门店数据"""
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        if hasattr(obj, 'store_id'):
            return obj.store_id == request.user.profile.store_id
        return True
