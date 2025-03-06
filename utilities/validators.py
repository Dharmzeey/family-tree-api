from rest_framework.response import Response
from rest_framework import status

def profile_check(request):
    try:
        profile = request.user.user_profile
        return profile
    except AttributeError:
        return None