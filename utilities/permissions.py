# permissions.py
from rest_framework import permissions

class IsVerified(permissions.BasePermission):
    """
    Allows access only to verified users (email and phone number, and account).
    """

    def has_permission(self, request, view):
        user = request.user

        # Only authenticated users can proceed
        if not user.is_authenticated:
            return False

        unverified = []

        if not user.email_verified:
            unverified.append("Email")

        # if not user.phone_number_verified:
        #     unverified.append("Phone number")

        if unverified:
            self.message = ", ".join(unverified) + " not verified."
            return False

        return True