import uuid
from django.db import models
from profiles.models import Profile

# Families must exist before you can have a family head and others

class Family(models.Model):
    uuid = models.UUIDField(editable=False, default=uuid.uuid4, unique=True)
    author = models.OneToOneField(Profile, on_delete=models.SET_NULL, null=True, related_name="family_author")
    name = models.CharField(max_length=255, unique=True)
    approved = models.BooleanField(default=False)


    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Families"

    
class Handler(models.Model):
    uuid = models.UUIDField(editable=False, default=uuid.uuid4, unique=True)
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name="family_handlers")
    operator = models.OneToOneField(Profile, on_delete=models.SET_NULL, null=True, related_name="operator_handler")

    class Meta:
        unique_together = ("family", "operator")

    def __str__(self):
        return f"{self.operator} is an operator for {self.family} family"
    

class Origin(models.Model):
    uuid = models.UUIDField(editable=False, default=uuid.uuid4, unique=True)
    family = models.OneToOneField(Family, on_delete=models.CASCADE, related_name="family_origin")
    details = models.TextField()

    def __str__(self):
        return f"{self.family} is from {self.details[:30]}..." if len(self.details) > 30 else f"{self.family} is from {self.details}"

class HouseInfo(models.Model):
    uuid = models.UUIDField(editable=False, default=uuid.uuid4, unique=True)
    family = models.OneToOneField(Family, on_delete=models.CASCADE, related_name="family_house_info")
    details = models.TextField()

    def __str__(self):
        return f"{self.family} is from {self.details[:30]}..." if len(self.details) > 30 else f"{self.family} is from {self.details}"


class BeliefSystem(models.Model):
    uuid = models.UUIDField(editable=False, default=uuid.uuid4, unique=True)
    family = models.OneToOneField(Family, on_delete=models.CASCADE, related_name="family_belief_system")
    details = models.TextField()

    def __str__(self):
        return f"{self.family} has {self.details[:30]}..." if len(self.details) > 30 else f"{self.family} has {self.details}"


class OtherInformation(models.Model):
    uuid = models.UUIDField(editable=False, default=uuid.uuid4, unique=True)
    family = models.OneToOneField(Family, on_delete=models.CASCADE, related_name="family_other_information")
    details = models.TextField()

    def __str__(self):
        return f"{self.family} --- {self.details[:30]}..." if len(self.details) > 30 else f"{self.family} --- {self.details}"

class Eulogy(models.Model):
    uuid = models.UUIDField(editable=False, default=uuid.uuid4, unique=True)
    family = models.OneToOneField(Family, on_delete=models.CASCADE, related_name="family_eulogy")
    details = models.TextField()

    def __str__(self):
        return f"{self.family} --- {self.details[:30]}..." if len(self.details) > 30 else f"{self.family} --- {self.details}"
    
    class Meta:
        verbose_name_plural = "Eulogies"

class FamilyHead(models.Model):
    uuid = models.UUIDField(editable=False, default=uuid.uuid4, unique=True)
    family = models.ForeignKey(Family, on_delete=models.SET_NULL, null=True, related_name="family_heads")
    person = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="family_head_person")
    comment = models.TextField() # Extra information about the person
    date_from = models.DateField()
    date_to = models.DateField(null=True, blank=True)  # Nullable for active leaders

    class Meta:
        unique_together = ("family", "person")
        ordering = ["date_to"]

    @property
    def still_on_throne(self):
        return self.date_to is None  # True if no end date (still in service)

    def __str__(self):
        return f"{self.person.first_name} {self.person.last_name} head of '{self.family}' family,  from {self.date_from} to {'Present' if self.still_on_throne else self.date_to}"
