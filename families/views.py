from django.db import IntegrityError
from django.core.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from utilities.error_handler import render_errors
from utilities.validators import profile_check
from profiles.models import Profile
from .models import Family, FamilyHead, Handler, Origin, HouseInfo, BeliefSystem, Eulogy, OtherInformation
from .serializers import FamilySerializer, HandlerSerializer, OriginSerializer, HouseInfoSerializer, BeliefSystemSerializer, OtherInformationSerializer, EulogySerializer, FamilyHeadSerializer

# I am thinking that create Family shoule be done from dev's end, I mean they will fill a kind of request, then the superuser can do the creation
class CreateFamilyView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        profile = profile_check(request)
        serializer = FamilySerializer(data=request.data)

        if serializer.is_valid():
            try:
                serializer.save(author=profile)
                data = {"message": "The family has been created and submitted for approval"}
                return Response(data, status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response({"error": "You cannot author for more than one family"}, status=status.HTTP_409_CONFLICT)

        return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

create_family = CreateFamilyView.as_view()


class ViewFamilyView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, family_id):
        profile_check(request)

        try:
            family = Family.objects.get(uuid=family_id)
            serializer = FamilySerializer(family)
            data = {"data": serializer.data, "message": "Family Retrieved"}
            return Response(data, status=status.HTTP_200_OK)
        
        except Family.DoesNotExist:
            return Response({"error": "Family Does not Exist"}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError:
            return Response(
                {"error": "Invalid family id"},
                status=status.HTTP_400_BAD_REQUEST,
            )

view_family = ViewFamilyView.as_view()


class UpdateFamilyView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, family_id):
        profile = profile_check(request)

        try:
            family = Family.objects.get(uuid=family_id)
        except Family.DoesNotExist:
            return Response({"error": "Family not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if the user is the author or a handler
        if (profile != family.author) and (profile not in [handler.operator for handler in family.family_handlers.all()]):
            return Response({"error": "You are not authorized to update this family"}, status=status.HTTP_403_FORBIDDEN)

        serializer = FamilySerializer(family, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Family details updated successfully"}, status=status.HTTP_200_OK)

        return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

update_family = UpdateFamilyView.as_view()


class AddHandlerView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        profile = profile_check(request)
        operator_id = request.data.get("operator_id")
        try:
            family = Family.objects.get(author=profile)
        except Family.DoesNotExist:
            return Response({"error": "You are not an author of any family"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            operator = Profile.objects.get(uuid=operator_id)
        except Profile.DoesNotExist:
            return Response({"error": "Profile with this id does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError:
            return Response({"error": "Invalid Operator ID sent"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            Handler.objects.create(family=family, operator=operator)
        except IntegrityError:
            return Response({"error": "This person is already your handler"}, status=status.HTTP_409_CONFLICT)
        return Response({"message": "Handler added successfully"}, status=status.HTTP_201_CREATED)
    
add_handler = AddHandlerView.as_view()


class AddOriginView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, family_id):
        profile = profile_check(request)

        try:
            family = Family.objects.get(uuid=family_id)
        except Family.DoesNotExist:
            return Response({"error": "Family not found"}, status=status.HTTP_404_NOT_FOUND)

        # Ensure only the author or handlers can add origin
        if (profile != family.author) and (profile not in [handler.operator for handler in family.family_handlers.all()]):
            return Response({"error": "You are not authorized to add origin"}, status=status.HTTP_403_FORBIDDEN)

        if hasattr(family, "family_origin"):
            return Response({"error": "Origin already exists for this family"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = OriginSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(family=family)
            return Response({"message": "Origin added successfully"}, status=status.HTTP_201_CREATED)

        return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
add_origin = AddOriginView.as_view()    


class AddHouseInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, family_id):
        profile = profile_check(request)

        try:
            family = Family.objects.get(uuid=family_id)
        except Family.DoesNotExist:
            return Response({"error": "Family not found"}, status=status.HTTP_404_NOT_FOUND)

        # Ensure only the author or handlers can add house info
        if (profile != family.author) and (profile not in [handler.operator for handler in family.family_handlers.all()]):
            return Response({"error": "You are not authorized to add house info"}, status=status.HTTP_403_FORBIDDEN)

        if hasattr(family, "family_house_info"):
            return Response({"error": "House info already exists for this family"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = HouseInfoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(family=family)
            return Response({"message": "House info added successfully"}, status=status.HTTP_201_CREATED)

        return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

add_house_info = AddHouseInfoView.as_view()


class AddBeliefSystemView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, family_id):
        profile = profile_check(request)

        try:
            family = Family.objects.get(uuid=family_id)
        except Family.DoesNotExist:
            return Response({"error": "Family not found"}, status=status.HTTP_404_NOT_FOUND)

        # Ensure only the author or handlers can add belief system
        if (profile != family.author) and (profile not in [handler.operator for handler in family.family_handlers.all()]):
            return Response({"error": "You are not authorized to add belief system"}, status=status.HTTP_403_FORBIDDEN)

        if hasattr(family, "family_belief_system"):
            return Response({"error": "Belief system already exists for this family"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = BeliefSystemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(family=family)
            return Response({"message": "Belief system added successfully"}, status=status.HTTP_201_CREATED)

        return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

add_belief_system = AddBeliefSystemView.as_view()


class AddOtherInformationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, family_id):
        profile = profile_check(request)

        try:
            family = Family.objects.get(uuid=family_id)
        except Family.DoesNotExist:
            return Response({"error": "Family not found"}, status=status.HTTP_404_NOT_FOUND)

        # Ensure only the author or handlers can add other information
        if (profile != family.author) and (profile not in [handler.operator for handler in family.family_handlers.all()]):
            return Response({"error": "You are not authorized to add other information"}, status=status.HTTP_403_FORBIDDEN)

        if hasattr(family, "family_other_information"):
            return Response({"error": "Other information already exists for this family"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = OtherInformationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(family=family)
            return Response({"message": "Other information added successfully"}, status=status.HTTP_201_CREATED)

        return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

add_other_information = AddOtherInformationView.as_view()


class AddEulogyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, family_id):
        profile = profile_check(request)

        try:
            family = Family.objects.get(uuid=family_id)
        except Family.DoesNotExist:
            return Response({"error": "Family not found"}, status=status.HTTP_404_NOT_FOUND)

        # Ensure only the author or handlers can add eulogy
        if (profile != family.author) and (profile not in [handler.operator for handler in family.family_handlers.all()]):
            return Response({"error": "You are not authorized to add eulogy"}, status=status.HTTP_403_FORBIDDEN)

        if hasattr(family, "family_eulogy"):
            return Response({"error": "Eulogy already exists for this family"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = EulogySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(family=family)
            return Response({"message": "Eulogy added successfully"}, status=status.HTTP_201_CREATED)

        return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

add_eulogy = AddEulogyView.as_view()


class AddFamilyHeadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, family_id):
        profile = profile_check(request)  # Ensure authenticated profile

        try:
            family = Family.objects.get(uuid=family_id)
        except Family.DoesNotExist:
            return Response({"error": "Family not found"}, status=status.HTTP_404_NOT_FOUND)

        # Ensure only the author or handlers can add a family head
        if (profile != family.author) and (profile not in [handler.operator for handler in family.family_handlers.all()]):
            return Response({"error": "You are not authorized to add a family head"}, status=status.HTTP_403_FORBIDDEN)

        serializer = FamilyHeadSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save(family=family)
            except IntegrityError:
                return Response({"error": "This person is already a family head"}, status=status.HTTP_409_CONFLICT)
            return Response({"message": "Family head added successfully"}, status=status.HTTP_201_CREATED)

        return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

add_family_head = AddFamilyHeadView.as_view()

