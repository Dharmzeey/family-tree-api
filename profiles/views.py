from django.db import IntegrityError
from django.db.models import Q
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from utilities.validators import profile_check
from .models import Profile, FamilyRelation, OnlineRelative, OfflineRelative, BondRequestNotification
from .serializers import ProfileSerializer, OnlineRelativeSerializer, RelationSerializer, OfflineRelativeSerializer, BondRequestNotificationSerializer
from utilities.pagiation import CustomPagination
from families.models import Family
from families.serializers import FamilySerializer


class CreateProfileView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = ProfileSerializer
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save(user=request.user)
            except IntegrityError:
                data = {"error": "User profile already exists"}
                return Response(data, status=status.HTTP_409_CONFLICT)      
            data = {"data": serializer.data, "message": "Profile Created"}
            return Response(data, status=status.HTTP_201_CREATED)
        return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
create_profile = CreateProfileView.as_view()


class ViewProfileView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            profile = request.user.user_profile
        except AttributeError:
            return Response(
                {"error": "Profile does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = ProfileSerializer(profile, context={'request': request})
        data = {"data": serializer.data, "message": "Profile Retrieved"}
        return Response(data, status=status.HTTP_200_OK)

view_profile = ViewProfileView.as_view()


class EditProfileView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer

    def put(self, request):
        if not (profile := profile_check(request)):
            return Response({"error": "Profile does not exist. Please create a profile first."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(profile, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            data = {"data": serializer.data, "message": "Profile Updated"}
            return Response(data, status=status.HTTP_200_OK)
        return Response(
            {"errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

edit_profile = EditProfileView.as_view()


class GetRelations(ListAPIView):
    """
    Fetches all the relations in the DB (e.g., Father, Mother, Sister, Brother, etc.)
    and returns them wrapped in a "data" key.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = RelationSerializer
    queryset = FamilyRelation.objects.all()

    def list(self, request, *args, **kwargs):
        # Get the default response from the parent class
        response = super().list(request, *args, **kwargs)

        # Wrap the response data in a "data" key
        wrapped_response = {"data": response.data}

        # Return the modified response
        return Response(wrapped_response)

get_relations = GetRelations.as_view()


class SearchRelatives(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get(self, request):
        search_query = request.query_params.get("query", "").strip()

        if not search_query:
            return Response(
                {"error": "Search query is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        profiles = Profile.objects.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(lineage_name__icontains=search_query)
        ).exclude(user=request.user)  # Exclude the current user from the results

        if not profiles.exists():
            return Response(
                {"error": "No matching profiles found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        paginator = self.pagination_class()

        paginated_profiles = paginator.paginate_queryset(profiles, request)
        serializer = ProfileSerializer(paginated_profiles, many=True, context={'request': request})
        
        return paginator.get_paginated_response(serializer.data)

search_relatives = SearchRelatives.as_view()


class CreateRelationsView(APIView):
    # This will evaluate and then send notification to the other account
    permission_classes = [IsAuthenticated]
    # serializer_class = RelativeSerializer
    def post(self, request):
        # Get the current user's profile
        if not (user_profile := profile_check(request)):
            return Response({"error": "Profile does not exist. Please create a profile first."}, status=status.HTTP_404_NOT_FOUND)
        # serializer = self.serializer_class(data=request.data)
        relative_id = request.data.get("relative_id")
        relation_id = request.data.get("relation_id")

        if not relative_id or not relation_id:
            return Response(
                {"error": "Both relative ID and relation ID are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )


        # Check the total number of relatives and offline relatives
        total_online_relatives = OnlineRelative.objects.filter(user=user_profile).count()
        total_offline_relatives = OfflineRelative.objects.filter(user=user_profile).count()
        total = total_online_relatives + total_offline_relatives

        if total > 15:
            return Response(
                {"error": "Maximum relative quota reached. You cannot add more relatives."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            relative_profile = Profile.objects.get(uuid=relative_id)
        except Profile.DoesNotExist:
            return Response(
                {"error": "Invalid relative ID."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            relation = FamilyRelation.objects.get(id=relation_id)
        except FamilyRelation.DoesNotExist:
            return Response(
                {"error": "Invalid relation ID."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if the relationship with user already exists by looking up if the user and a relative already exist in DB
        existing_relation = OnlineRelative.objects.filter(
            user=user_profile, relative=relative_profile
        ).exists()
        if existing_relation:
            return Response(
                {"error": "You already have a relationship with this Person."},
                status=status.HTTP_409_CONFLICT,
            )
        
        # This below will check if the notification already exists
        existing_bond_request = BondRequestNotification.objects.filter(
            sender=user_profile, receiver=relative_profile
        ).exists()
        if existing_bond_request:
            return Response(
                {"error": "A bond request has already been sent to this user."},
                status=status.HTTP_409_CONFLICT,
            )
        
        # This below will check if a Bond Request has been sent to a user with the "Mother" or "Father" relation 
        if relation.name in ["Father", "Mother"]:
            existing_parent_bond_request = BondRequestNotification.objects.filter(
            sender=user_profile, relation__name=relation.name
            ).exists()
            if existing_parent_bond_request:
                return Response(
                    {"error": f"Seriously? You can't send another {relation.name} request. One is enough."},
                    status=status.HTTP_409_CONFLICT,
                )


        # Check if the proposed relationship is Father or Mother and verify it is already existed becasue you cannot have more than one father and one mother
        if relation.name in ["Father", "Mother"]:
            existing_parent_relation = OnlineRelative.objects.filter(
                user=user_profile, relation__name=relation.name
            ).exists() or OfflineRelative.objects.filter(
                user=user_profile, relation__name=relation.name
            ).exists()
            if existing_parent_relation:
                return Response(
                    {"error": f"You cannot have more than one {relation.name}."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        
        # After the above check, now the notification is created
        # Create a bond request notification
        bond_request = BondRequestNotification.objects.create(
            sender=user_profile,
            receiver=relative_profile,
            relation=relation
        )
        bond_request.save()
        return Response(
            {"data": bond_request.uuid, "message": "Bond request sent successfully."},
            status=status.HTTP_201_CREATED,
        )
create_relation = CreateRelationsView.as_view()


class ViewBondRequests(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not (user_profile := profile_check(request)):
            return Response({"error": "Profile does not exist. Please create a profile first."}, status=status.HTTP_404_NOT_FOUND)


        # Fetch all bond requests sent to the current user
        bond_requests = BondRequestNotification.objects.filter(receiver=user_profile).select_related("sender", "relation")

        if not bond_requests.exists():
            return Response(
                {"error": "No bond requests found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = BondRequestNotificationSerializer(bond_requests, many=True, context={'request': request})
        return Response(
            {"data": serializer.data, "message": "Bond requests retrieved successfully."},
            status=status.HTTP_200_OK,
        )
view_bond_requests = ViewBondRequests.as_view()


class ProcessBondRequest(APIView):
    # User can either accept or reject a bond request
    # If accepted, the relationship will be created
    permission_classes = [IsAuthenticated]
    def post(self, request):
        if not (user_profile := profile_check(request)):
            return Response({"error": "Profile does not exist. Please create a profile first."}, status=status.HTTP_404_NOT_FOUND)

        bond_request_id = request.data.get("bond_request_id")
        accept = request.data.get("accept")

        if not bond_request_id or accept is None:
            return Response(
                {"error": "Both bond request ID and accept status are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            bond_request = BondRequestNotification.objects.get(uuid=bond_request_id, receiver=user_profile)
        except BondRequestNotification.DoesNotExist:
            return Response(
                {"error": "Invalid bond request ID."},
                status=status.HTTP_400_BAD_REQUEST,
            )           

        if accept:
            try:
                # Create a new relationship where the user will be the person that sent the request and relative will be the person accepting, so the relative is created at that person' end
                relative = OnlineRelative.objects.create(
                    user=bond_request.sender,
                    relative=user_profile,
                    relation=bond_request.relation
                )
                relative.save()
                bond_request.delete() # Removes the notification from DB after acceptance
            except IntegrityError:
                return Response(
                {"error": "This relationship with this user already exists."},
                status=status.HTTP_409_CONFLICT,
            )
        else: 
            bond_request.delete() # Removes the notification from DB when rejected
        
        return Response(
            {"message": "Bond request processed successfully."},
            status=status.HTTP_200_OK,
        )
process_bond_request = ProcessBondRequest.as_view()


class ViewRelatives(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not (user_profile := profile_check(request)):
            return Response({"error": "Profile does not exist. Please create a profile first."}, status=status.HTTP_404_NOT_FOUND)

        # Fetch all relatives of the current user
        relatives = OnlineRelative.objects.filter(user=user_profile).select_related("relative", "relation")
        offline_relatives = OfflineRelative.objects.filter(user=user_profile).select_related("relation")

        # Check if the user has any relatives
        if not relatives.exists() and not offline_relatives.exists():
            return Response(
                {"error": "No relatives found for this user."},
                status=status.HTTP_404_NOT_FOUND,
            )
        user_serializer = ProfileSerializer(user_profile, context={'request': request})
        serializer = OnlineRelativeSerializer(relatives, many=True, context={'request': request})
        offline_serializer = OfflineRelativeSerializer(offline_relatives, many=True, context={'request': request})

        return Response(
            {
                "data": {
                "user": user_serializer.data,
                "relatives": serializer.data,
                "offline_relatives": offline_serializer.data
            }, 
            "message": "Relatives retrieved successfully."
            },
            status=status.HTTP_200_OK,
        )
view_relatives = ViewRelatives.as_view()


class ViewUserRelatives(APIView):
    # This  view is similar to the one that fetch the logged in user relative, but rather the relatives of other user with uuid
    permission_classes = [IsAuthenticated]

    def get(self, request, relative_id):
        try:
            # The above gets (relative_id) the id of the "Online Relative" Model and not the "Profile" Model, the after the Online Relative is gotten, then the profile is the looked up
            online_relative_id = relative_id.split("_")[1] # This will rip off the "on_" and the "off_" prefix added by the serializer
            user_profile = OnlineRelative.objects.get(uuid=online_relative_id).relative # first check the online relative model and then get the profile
        except Profile.DoesNotExist:
            return Response(
                {"error": "User profile does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except ValidationError:
            return Response(
                {"error": "Invalid user id"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        # Fetch all relatives of the specified user
        relatives = OnlineRelative.objects.filter(user=user_profile).select_related("relative", "relation")
        offline_relatives = OfflineRelative.objects.filter(user=user_profile).select_related("relation")

        # Check if the user has any relatives
        if not relatives.exists() and not offline_relatives.exists():
            return Response(
                {"error": "No relatives found for this user."},
                status=status.HTTP_404_NOT_FOUND,
            )
        user_serializer = ProfileSerializer(user_profile, context={'request': request})
        online_serializer = OnlineRelativeSerializer(relatives, many=True, context={'request': request})
        offline_serializer = OfflineRelativeSerializer(offline_relatives, many=True, context={'request': request})

        return Response(
            {
                "data": {
                "user": user_serializer.data,
                "relatives": online_serializer.data,
                "offline_relatives": offline_serializer.data
            }, 
            "message": "Relatives retrieved successfully."
            },
            status=status.HTTP_200_OK,
        )
view_user_relatives = ViewUserRelatives.as_view()


class DeleteRelativeView(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self, request, relative_id):
        if not (user_profile := profile_check(request)):
            return Response({"error": "Profile does not exist. Please create a profile first."}, status=status.HTTP_404_NOT_FOUND)
        relative_status = relative_id.split("_")[0] #This will get if it is "on" or "off"
        try:
            if relative_status == "on":
                user_relative = OnlineRelative.objects.get(user=user_profile, uuid=relative_id.split("_")[1]) # the split extract the real uuid striping off the "on"
                user_relative.delete()
            elif relative_status == "off":
                user_relative = OfflineRelative.objects.get(user=user_profile, uuid=relative_id.split("_")[1]) # the split extract the real uuid striping off the "on"
                user_relative.delete()
            return Response(
                {
                    "message": "Relative deleted successfully"
                },
                status=status.HTTP_200_OK
            )
        except ValidationError:
            return Response(
                {"error": "Invalid user id"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except (OnlineRelative.DoesNotExist, OfflineRelative.DoesNotExist ):
            return Response(
                {
                    "error": "This selected relative does not belong to you, so you cannot modify"
                }, 
                status=status.HTTP_400_BAD_REQUEST
            )
delete_relative = DeleteRelativeView.as_view()
    

class AddOfflineRelative(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        if not (user_profile := profile_check(request)):
            return Response({"error": "Profile does not exist. Please create a profile first."}, status=status.HTTP_404_NOT_FOUND)
            
        # Check the total number of relatives and offline relatives
        total_relatives = OnlineRelative.objects.filter(user=user_profile).count()
        total_offline_relatives = OfflineRelative.objects.filter(user=user_profile).count()
        total = total_relatives + total_offline_relatives

        if total > 15:
            return Response(
                {"error": "Maximum relative quota reached. You cannot add more relatives."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = OfflineRelativeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            relation = serializer.validated_data['relation']
            # Check if the proposed relationship is Father or Mother and verify it is already existed becasue you cannot have more than one father and one mother
            if relation.name in ["Father", "Mother"]:
                existing_parent_relation = OnlineRelative.objects.filter(
                    user=user_profile, relation__name=relation.name
                ).exists() or OfflineRelative.objects.filter(
                    user=user_profile, relation__name=relation.name
                ).exists()
                if existing_parent_relation:
                    return Response(
                        {"error": f"You cannot have more than one {relation.name}."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            try:
                relative = serializer.save(user=user_profile)
                pass
            except IntegrityError:
                return Response(
                    {"error": "This relative already exists."},
                    status=status.HTTP_409_CONFLICT,
                )
            return Response(
                {"data": serializer.data, "message": "Relative added successfully."},
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )
add_offline_relative = AddOfflineRelative.as_view()


# This below is where the function to include an connet established family with user profile
class IncludeFamilyRequest(APIView):
    # This is just to show the user information about the family before the user finally adds the family, because there is no edit or delete
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not profile_check(request):
            return Response({"error": "Profile does not exist. Please create a profile first."}, status=status.HTTP_404_NOT_FOUND)
        family_id = request.data.get("family_id")
        try:
            family = Family.objects.get(uuid=family_id)
            serializer = FamilySerializer(family)
            return Response(
                {"message": "Are you sure you want to add this family to your profile ?", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        except Family.DoesNotExist:
            return Response(
                {"error": "Family does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except ValidationError:
            return Response(
                {"error": "Invalid ID supplied."},
                status=status.HTTP_404_NOT_FOUND,
            )
include_family_request = IncludeFamilyRequest.as_view()

    
class ConfirmFamilyRequest(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not (user_profile := profile_check(request)):
            return Response({"error": "Profile does not exist. Please create a profile first."}, status=status.HTTP_404_NOT_FOUND)
        family_id = request.data.get("family_id")

        if user_profile.family:
            return Response({"error": "You already have a linked family"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            family = Family.objects.get(uuid=family_id)
            print(family)
            user_profile.family = family
            user_profile.save()
            return Response(
                {"message": "Family included successfully."},
                status=status.HTTP_200_OK,
            )
        except Family.DoesNotExist:
            return Response(
                {"error": "Family does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except ValidationError:
            return Response(
                {"error": "Invalid ID supplied."},
                status=status.HTTP_404_NOT_FOUND,
            )
confirm_family_request = ConfirmFamilyRequest.as_view()