from rest_framework import serializers
from profiles.models import Profile
from .models import Family, FamilyHead, Handler, Origin, HouseInfo, BeliefSystem, Eulogy, OtherInformation


class FamilyHeadSerializer(serializers.ModelSerializer):

    id = serializers.SerializerMethodField()
    person = serializers.UUIDField()
    still_on_throne = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = FamilyHead
        exclude = "uuid", "family",

    def get_id(self, obj):
        return obj.uuid
    
    def get_still_on_throne(self, obj):
        return obj.still_on_throne 
    
    def create(self, validated_data):
        person_uuid = validated_data.pop("person")  # Extract person UUID
        try:
            person = Profile.objects.get(uuid=person_uuid)  # Get Profile instance
        except Profile.DoesNotExist:
            raise serializers.ValidationError({"person": "Profile with this UUID does not exist."})

        family_head = FamilyHead.objects.create(person=person, **validated_data)
        return family_head
    
    

class HandlerSerializer(serializers.ModelSerializer):

    id = serializers.SerializerMethodField()

    class Meta:
        model = Handler
        exclude = "uuid", "family",

    def get_id(self, obj):
        return obj.uuid
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['operator'] = f"{instance.operator.last_name} {instance.operator.first_name}"
        return representation    


class OriginSerializer(serializers.ModelSerializer):

    id = serializers.SerializerMethodField()

    class Meta:
        model = Origin
        exclude = "uuid", "family",

    def get_id(self, obj):
        return obj.uuid
    

class HouseInfoSerializer(serializers.ModelSerializer):

    id = serializers.SerializerMethodField()

    class Meta:
        model = HouseInfo
        exclude = "uuid", "family",

    def get_id(self, obj):
        return obj.uuid
    

class BeliefSystemSerializer(serializers.ModelSerializer):

    id = serializers.SerializerMethodField()

    class Meta:
        model = BeliefSystem
        exclude = "uuid", "family",

    def get_id(self, obj):
        return obj.uuid
    

class EulogySerializer(serializers.ModelSerializer):

    id = serializers.SerializerMethodField()

    class Meta:
        model = Eulogy
        exclude = "uuid", "family",

    def get_id(self, obj):
        return obj.uuid
    


class OtherInformationSerializer(serializers.ModelSerializer):

    id = serializers.SerializerMethodField()

    class Meta:
        model = OtherInformation
        exclude = "uuid", "family",

    def get_id(self, obj):
        return obj.uuid
    

class FamilySerializer(serializers.ModelSerializer):

    id = serializers.SerializerMethodField()

    family_heads = FamilyHeadSerializer(many=True, read_only=True)
    family_handlers = HandlerSerializer(many=True, read_only=True)
    family_origin = OriginSerializer(read_only=True)
    family_house_info = HouseInfoSerializer(read_only=True)
    family_belief_system = BeliefSystemSerializer(read_only=True)
    family_eulogy = EulogySerializer(read_only=True)
    family_other_information = OtherInformationSerializer(read_only=True)

    class Meta:
        model = Family
        exclude = ("uuid", "approved")
        read_only_fields = ["author"]
        # depth = 1

    def get_id(self, obj):
        return obj.uuid
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["author"] = f"{instance.author.last_name} {instance.author.first_name}"
        return representation
    