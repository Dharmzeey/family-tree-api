import uuid
from django.db import models
from django.core.exceptions import ValidationError
from authentication.models import User

def validate_image_size(image):
    MAX_IMAGE_SIZE = 850 * 1024  # 2MB
    if image.size > MAX_IMAGE_SIZE:
        raise ValidationError("Image size should not exceed 800kb.")


class Profile(models.Model):
	uuid = models.UUIDField(editable=False, default=uuid.uuid4, unique=True)
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user_profile")
	lineage_name = models.CharField(max_length=100, blank=True, null=True)
	last_name = models.CharField(max_length=150, null=False)
	first_name = models.CharField(max_length=150, null=False)	
	other_name = models.CharField(max_length=100, blank=True, null=True)
	picture = models.ImageField(upload_to="images", default="avatar.png", validators=[validate_image_size])
	
	def __str__(self):
		return f"{self.last_name} {self.first_name} {self.other_name}"
	
	class Meta:
		ordering = ['last_name']
	


class FamilyRelation(models.Model):
	"""
	This will hold data for the likes of Father, Mother, Sister, Brother etc.
	Will be populated by the developer
	"""
	name = models.CharField(max_length=30, unique=True)

	class Meta:
		ordering = ['-name']

	def __str__(self):
		return self.name
	

class OnlineRelative(models.Model):
	uuid = models.UUIDField(editable=False, default=uuid.uuid4, unique=True)
	user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="user_relative") # The current logged in user
	relative = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="relative_relative") # The person the user is related to
	relation = models.ForeignKey(FamilyRelation, on_delete=models.SET_NULL, related_name="relation_relative", null=True) # How is the person related to the user
	
	class Meta:
		unique_together = ("user", "relative")

	def __str__(self):
		return f"{self.user} is a {self.relation} to {self.relative}"
	

class OfflineRelative(models.Model):
	"""
	This will be used to store relatives that are not registered on the platform
	"""
	uuid = models.UUIDField(editable=False, default=uuid.uuid4, unique=True)
	user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="user_offline_relative") # The current logged in user
	first_name = models.CharField(max_length=150, null=False)
	last_name = models.CharField(max_length=150, null=False)
	other_name = models.CharField(max_length=100, blank=True, null=True)
	picture = models.ImageField(upload_to="images", default="avatar.png", validators=[validate_image_size], blank=True, null=True)
	relation = models.ForeignKey(FamilyRelation, on_delete=models.SET_NULL, related_name="relation_offline_relative", null=True) # How is the person related to the user
	
	class Meta:
		unique_together = ("user", "first_name", "last_name")

	def __str__(self):
		return f"{self.user} is a {self.relation} to {self.last_name} {self.first_name}"
	

class BondRequestNotification(models.Model):
	"""
	When a user sends a bond request to another user, this model will be used to store the request
	"""
	uuid = models.UUIDField(editable=False, default=uuid.uuid4, unique=True)
	sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="sender_bond_request") # The person sending the request
	receiver = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="receiver_bond_request") # The person receiving the request
	relation = models.ForeignKey(FamilyRelation, on_delete=models.SET_NULL, related_name="relationship_bond_request", null=True) # The relationship the sender wants to establish with the receiver
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	accepted = models.BooleanField(default=False)
	
	class Meta:
		unique_together = ("sender", "receiver")
		ordering = ['-created_at']

	def __str__(self):
		return f"{self.sender} sent a bond request to {self.receiver}"