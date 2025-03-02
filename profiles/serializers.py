from django.db.models import Q
from rest_framework import serializers
from .models import Profile, OnlineRelative, FamilyRelation, OfflineRelative, BondRequestNotification
from families.models import Family

class ProfileSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    family_id = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        exclude = ("uuid", "user", "family")
        read_only_fields = ["user"]

    def get_id(self, obj):
        return obj.uuid

    def get_family_id(self, obj):
        family = Family.objects.filter(
            Q(author=obj) | Q(family_handlers__operator=obj) | Q(family_profile=obj)
        ).distinct().first()

        return family.uuid if family else None


class RelationSerializer(serializers.ModelSerializer):
    class Meta:
        model = FamilyRelation
        fields = "__all__"


class BondRequestNotificationSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    lineage_name = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    picture = serializers.SerializerMethodField()
    class Meta:
        model = BondRequestNotification
        exclude = ("uuid", "created_at", "updated_at")

    def get_id(self, obj):
        return obj.uuid
    
    def get_lineage_name(self, obj):
        return obj.sender.lineage_name

    def get_full_name(self, obj):
        full_name = f"{obj.sender.last_name} {obj.sender.first_name} {obj.sender.other_name}"
        return full_name

    def get_picture(self, obj):
        request = self.context.get('request')
        if obj.sender.picture:
            return request.build_absolute_uri(obj.sender.picture.url)
        return None
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['sender'] = instance.sender.first_name
        representation['relation'] = instance.relation.name
        return representation


class OnlineRelativeSerializer(serializers.ModelSerializer):

    id = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    other_name = serializers.SerializerMethodField()
    picture = serializers.SerializerMethodField()

    has_relatives = serializers.SerializerMethodField() # This field will hold boolean for if the current relative that is being displayed as a relative to the CENTRAL user also has any associated relative. This will help to show a button "VIEW RELATIVE" on the relative card. The get_has_relativse() fn does the work

    class Meta:
        model = OnlineRelative
        exclude = ("user", "relative", "uuid") # Keep user and relative read-only
        read_only_fields = ["user"]
    
    # This below is because this and offline serializer are sent together so to be able to differentiate
    def get_id(self, obj):
        return f"on_{obj.uuid}"

    def get_first_name(self, obj):
        return obj.relative.first_name
    
    def get_last_name(self, obj):
        return obj.relative.last_name
    
    def get_other_name(self, obj):
        return obj.relative.other_name
        
    def get_picture(self, obj):
        request = self.context.get('request')
        if obj.relative.picture:
            return request.build_absolute_uri(obj.relative.picture.url)
        return None
    
    def get_has_relatives(self, obj):
        # If A (obj) is the central profile being checked, and B, C, D, E (.relatives) are the relatives to A. so to know if B, C, D and E also have relatives (.user_relative) associated with them is what the method checks.

        # The obj.relative will hold the Profile Model accessed from the OnlineRelative Model, then the .user_relative will use the reverse lookup from Profile-> OnlineRelative to fetch all the OnlineRelative which the user has.
        return obj.relative.user_relative.exists()
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['relation'] = instance.relation.name
        return representation


class OfflineRelativeSerializer(serializers.ModelSerializer):

    id = serializers.SerializerMethodField()

    class Meta:
        model = OfflineRelative
        exclude = ("user","uuid")  # Keep user read-only
        read_only_fields = ["user",]

    def validate(self, data):
        # Check if 'relation' is present in the input data
        if 'relation' not in data:
            raise serializers.ValidationError({"relation": "This field is required."})
        return data        


    # This below is because this and online serializer are sent together so to be able to differentiate
    def get_id(self, obj):
        return f"off_{obj.uuid}"
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['relation'] = instance.relation.name
        return representation


# class OfflineRelativeSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = OfflineRelative
#         exclude = ("user",)  # Keep user read-only
#         read_only_fields = ["user",]

#     def to_representation(self, instance):
#         # Call the parent method to get the default representation
#         representation = super().to_representation(instance)

#         # Check if 'relation' exists as a key in the representation
#         # If not, try to fetch it from the instance
#         if isinstance(instance, dict):  # Check if instance is a dictionary
#             relation_name = instance.get('relation', {}).get('name', None)
#         else:  # Assume instance is a model instance
#             relation_name = getattr(instance.relation, 'name', None)

#         # Add the 'relation' field to the representation
#         representation['relation'] = relation_name

#         return representation