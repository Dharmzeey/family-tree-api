from rest_framework import status
from rest_framework.response import Response
from profiles.models import Profile

class UserProfileRequiredMixin:
    """
    Mixin to ensure the user has a profile before proceeding.
    """
    def check_user_profile(self):
        try:
            return self.request.user.user_profile
        except Profile.DoesNotExist:
            return None

    def dispatch(self, request, *args, **kwargs):
        user_profile = self.check_user_profile()
        if not user_profile:
            return Response(
                {"error": "User profile does not exist. Please create a profile first."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return super().dispatch(request, *args, **kwargs)