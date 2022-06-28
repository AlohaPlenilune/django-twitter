from rest_framework.permissions import BasePermission

class IsObjectOwner(BasePermission):
    # This permission is used to check if object.user == request.user
    # This is a general class, can be put in a shared location if it will be used in other place.
    # Permissions will be executed one by one.
    # if the action detail == False, only check if has_permission
    # if the action detail == True, check both has_permission and has_object_permission
    # if there is error, the default message will show the content of IsObjectOwner.message

    message = 'You do not have permission to access this object.'

    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        return request.user == obj.user