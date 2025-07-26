from rest_framework import permissions


class IsModer(permissions.BasePermission):
    message = 'Adding and deleting courses and lessons not allowed'

    def has_permission(self, request, view):
        return request.user.groups.filter(name='moders').exists()
