from django.contrib import admin
from .models import Profile, Relative, FamilyRelation, OfflineRelative

admin.site.register(Profile)
admin.site.register(Relative)
admin.site.register(OfflineRelative)
admin.site.register(FamilyRelation)