import random
import string
import pytz
from datetime import datetime
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login
from django.conf import settings
from django.db import IntegrityError
from django.db.models import Q
from rest_framework import status
from django.contrib.auth import get_user_model
from django.core.cache import caches
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
# from authentication.backends import EmailOrPhoneBackend

from utilities.error_handler import render_errors
from families.models import Family, Handler

from . import serializers as CustomSerializers

User = get_user_model()


email_verification_cache = caches['email_verification']
password_reset_cache = caches['password_reset']

def generate_reset_token():
  return ''.join(random.choices(string.ascii_letters + string.digits, k=64))

def handle_send_email(user):
    pin = str(random.randint(100000, 999999))
    send_mail(
    'Family Tree Email Verification',
    f'Hello 👋.\nYour verification PIN is {pin}. \nIt will expire in 10 minutes',
    settings.DEFAULT_FROM_EMAIL,
    [user.email],
    fail_silently=False,
    )
    
    email_verification_cache.set(
            f"email_verification:{user.email}", 
            {
                'email_pin': pin,
                'timestamp': datetime.now(pytz.UTC).timestamp(),
                'verified': False  # Track if PIN has been verified
            },
            timeout=600  # 10 minutes
        )
  

class UserCreateView(APIView):
  serializer_class = CustomSerializers.UserSerializer
  def post(self, request):
    serializer = self.serializer_class(data=request.data)
    if serializer.is_valid():
      try:
        user = serializer.save()
        tokens = TokenObtainPairSerializer().validate(request.data)
        access_token = tokens['access']
        refresh_token = tokens['refresh']
        login(request, user, backend="authentication.backends.EmailOrPhoneBackend")
        user_serializer = CustomSerializers.UserSerializer(instance=user)
        data = {
          'access_token': access_token,
          'refresh_token': refresh_token,
          'data': user_serializer.data
        }
        # login(request, user)
        # handle_send_email(user) # This sends code to user after registering
        return Response(data, status=status.HTTP_201_CREATED)
      except IntegrityError:
        return Response({'error': 'User with this email or Phone Number already exists.'}, status=status.HTTP_409_CONFLICT)
    data = {"errors": render_errors(serializer.errors)}
    return Response(data, status=status.HTTP_400_BAD_REQUEST)
user_create = UserCreateView.as_view()


class UserLoginView(APIView):
    serializer_class = CustomSerializers.UserLoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response({"errors": render_errors(serializer.errors)}, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data.get("email")
        phone_number = serializer.validated_data.get("phone_number")
        password = serializer.validated_data.get("password")

        if not email and not phone_number:
            return Response({"error": "Email or phone number is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email__iexact=email) if email is not None else User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)

        user = authenticate(request=request, email=user.email, password=password)
        if user is None:
            return Response({"error": "Invalid Credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        login(request, user, backend="authentication.backends.EmailOrPhoneBackend")
        refresh = RefreshToken.for_user(user)
        family = Family.objects.filter(
            Q(author__user=user) | Q(family_handlers__operator__user=user)
                ).distinct().first()

        if family:
            is_author = family.author and family.author.user == user
            is_handler = family.family_handlers.filter(operator__user=user).exists() # Reverse lookup
        else:
            is_author = is_handler = False

        data = {
            "data": {
                "is_author": is_author,
                "is_handler": is_handler,
                "family_id": family.uuid if family else None,
            },
           "access_token": str(refresh.access_token),
           "refresh_token": str(refresh)
        }
        return Response(data, status=status.HTTP_200_OK)

user_login = UserLoginView.as_view()


class SendEmailVerificationView(APIView):
  permission_classes = [IsAuthenticated]    
  def post(self, request):
    user = request.user
    if user.email_verified:
      return Response({"error": "Email has already been verified"}, status=status.HTTP_201_CREATED)        
    existing_data = email_verification_cache.get(f"email_verification:{user.email}")
    if existing_data:
        return Response(
            {"error": "Email Verification already sent"}, 
                status=status.HTTP_409_CONFLICT
            )
    handle_send_email(user)
    return Response({"message": "Verification PIN expired. New PIN sent to email."}, status=status.HTTP_200_OK) 
send_email_verificiation = SendEmailVerificationView.as_view()


class VerifyEmailView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CustomSerializers.EmailVeriificationSerializer
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user=request.user
            cached_data = email_verification_cache.get(f"email_verification:{user.email}")
            if not cached_data:
                return Response(
                    {"error": "Email verification PIN expired or has not been sent"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            if cached_data['email_pin'] == serializer.data['email_pin']:
                user.email_verified = True
                user.save()
                email_verification_cache.delete(f"email_verification:{user.email}")
                return Response({"message": "Email verified successfully"}, status=status.HTTP_200_OK)
            elif cached_data['email_pin'] != serializer.data['email_pin']:
                return Response({"error": "Invalid PIN"}, status=status.HTTP_403_FORBIDDEN)
        return Response({"errors": render_errors(serializer.errors)}, status=status.HTTP_400_BAD_REQUEST)
verify_email = VerifyEmailView.as_view()


class SendPhoneVerificationView(APIView):
  def post(self, request):
    return Response()


class VerifyPhoneView(APIView):
  def post(self, request):
    return Response()
verify_phone = VerifyPhoneView.as_view()


class RequestPasswordResetView(APIView):
    def post(self, request):
        serializer_class = CustomSerializers.RequestPasswordResetSerializer
        serializer = serializer_class(data=request.data)
        
        if serializer.is_valid():
            try:
                user = User.objects.get(
                    email=serializer.validated_data['email'],
                    # phone_number=serializer.validated_data['phone_number']
                )
                
                # Check if PIN already exists in cache
                existing_data = password_reset_cache.get(f"password_reset:{user.email}")
                if existing_data:
                    return Response(
                        {"error": "password reset PIN already sent"}, 
                        status=status.HTTP_409_CONFLICT
                    )

                # Generate PIN and token
                email_pin = str(random.randint(100000, 999999))
                reset_token = generate_reset_token()
                
                # Send email
                # send_mail(
                #     'Kwiseworld password reset',
                #     f'Hello 👋\nYour password reset PIN is {email_pin}. \nIt will expire in 10 minutes',
                #     settings.DEFAULT_FROM_EMAIL,
                #     [user.email],
                #     fail_silently=False,
                # )

                # Store in cache with 10 minutes expiration
                password_reset_cache.set(
                    f"password_reset:{user.email}", 
                    {
                        'email_pin': email_pin,
                        'reset_token': reset_token,
                        'phone_number': user.phone_number,
                        'timestamp': datetime.now(pytz.UTC).timestamp(),
                        'verified': False  # Track if PIN has been verified
                    },
                    timeout=600  # 10 minutes
                )

                return Response({
                    "message": "Password reset PIN sent to email",
                    "reset_token": reset_token  # Return token to client
                }, status=status.HTTP_200_OK)
                
            except User.DoesNotExist:
                return Response(
                    {"error": "User information not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        return Response(
            {"errors": render_errors(serializer.errors)}, 
            status=status.HTTP_400_BAD_REQUEST
        )

request_password_reset = RequestPasswordResetView.as_view()


class VerifyPasswordResetPinView(APIView):
    def post(self, request):
        serializer = CustomSerializers.VerifyPasswordResetPinSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            # phone_number = serializer.validated_data['phone_number']
            submitted_pin = serializer.validated_data['email_pin']
            reset_token = serializer.validated_data.get('reset_token') 

            # Get stored data from cache
            cached_data = password_reset_cache.get(f"password_reset:{email}")
            
            if not cached_data:
                return Response(
                    {"error": "password reset PIN expired or has not been sent"}, 
                    status=status.HTTP_404_NOT_FOUND
                )

            # Verify token
            if cached_data['reset_token'] != reset_token:
                return Response(
                    {"error": "Invalid reset token"}, 
                    status=status.HTTP_403_FORBIDDEN
                )

            # Verify phone number
            # if cached_data['phone_number'] != phone_number:
            #     return Response(
            #         {"error": "User information not found"}, 
            #         status=status.HTTP_404_NOT_FOUND
            #     )

            # Check expiration
            timestamp = cached_data['timestamp']
            if (datetime.now(pytz.UTC).timestamp() - timestamp) > 600:  # 10 minutes
                password_reset_cache.delete(f"password_reset:{email}")
                return Response(
                    {"error": "Password reset PIN expired"}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )

            # Verify PIN
            if cached_data['email_pin'] != submitted_pin:
                return Response(
                    {"error": "Invalid PIN"}, 
                    status=status.HTTP_403_FORBIDDEN
                )

            # Generate new token for password reset which will replace for the password request and be needed for password reset
            reset_token = generate_reset_token()
            
            # Update cache with new token and mark as verified then initiate the password_verify
            cached_data['reset_token'] = reset_token
            cached_data['verified'] = True
            password_reset_cache.set(
                f"password_verify:{email}",
                cached_data,
                timeout=600  # Reset timeout for another 10 minutes
            )
            # clears the data from password_reset
            password_reset_cache.delete(f"password_reset:{email}")

            return Response({
                "message": "Password reset PIN verified successfully",
                "reset_token": reset_token
            }, status=status.HTTP_200_OK)
            
        return Response(
            {"errors": render_errors(serializer.errors)}, 
            status=status.HTTP_400_BAD_REQUEST
        )

verify_password_reset_pin = VerifyPasswordResetPinView.as_view()        
        

class CreateNewPasswordView(APIView):
    def post(self, request):
        serializer = CustomSerializers.CreateNewPasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            # phone_number = serializer.validated_data['phone_number']
            reset_token = serializer.validated_data.get('reset_token')  # Get reset token
            new_password = serializer.validated_data['password']

            try:
                # user = User.objects.get(email=email, phone_number=phone_number)
                user = User.objects.get(email=email)
                cached_data = password_reset_cache.get(f"password_verify:{email}")
                
                if not cached_data:
                    return Response(
                        {"error": "Password reset session expired or invalid"}, 
                        status=status.HTTP_403_FORBIDDEN
                    )

                # Verify reset token and PIN verification status
                if (not cached_data['verified'] or 
                    cached_data['reset_token'] != reset_token):
                    return Response(
                        {"error": "Invalid reset token or PIN not verified"}, 
                        status=status.HTTP_403_FORBIDDEN
                    )
                user.set_password(new_password)
                user.save()
                password_reset_cache.delete(f"password_verify:{email}")            
                return Response(
                    {"message": "password changed successfully"}, 
                    status=status.HTTP_200_OK
                )
                
            except User.DoesNotExist:
                return Response(
                    {"error": "User information not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
                
        return Response(
            {"errors": render_errors(serializer.errors)}, 
            status=status.HTTP_400_BAD_REQUEST
        )
create_new_password = CreateNewPasswordView.as_view()


class LogoutView(APIView):
  permission_classes = [IsAuthenticated]
  def post(self, request):
    try:
        refresh_token = request.data["refresh_token"]
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response(status=205)
    except Exception:
        return Response(status=400)
logout = LogoutView.as_view()