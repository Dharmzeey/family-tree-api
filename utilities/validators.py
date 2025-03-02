from rest_framework.response import Response
from rest_framework import status

def profile_check(request):
    try:
        profile = request.user.user_profile
        return profile
    except AttributeError:
        return None
        # return Response(
        #     {"error": "Profile does not exist. Please create a profile first."},
        #     status=status.HTTP_404_NOT_FOUND,
        # )