from rest_framework import serializers
from .models import Profile, Relative, FamilyRelation, OfflineRelative

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = "__all__"
        read_only_fields = ["user"]


class RelationSerializer(serializers.ModelSerializer):
    class Meta:
        model = FamilyRelation
        fields = "__all__"


class RelativeSerializer(serializers.ModelSerializer):

    id = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    other_name = serializers.SerializerMethodField()
    picture = serializers.SerializerMethodField()

    class Meta:
        model = Relative
        exclude = ("user", "relative") # Keep user and relative read-only
        read_only_fields = ["user"]
    
    def get_id(self, obj):
        return f"on_{obj.id}"

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
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['relation'] = instance.relation.name
        return representation


class OfflineRelativeSerializer(serializers.ModelSerializer):

    id = serializers.SerializerMethodField()

    class Meta:
        model = OfflineRelative
        exclude = ("user",)  # Keep user read-only
        read_only_fields = ["user",]

    def get_id(self, obj):
        return f"off_{obj.id}"
    
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