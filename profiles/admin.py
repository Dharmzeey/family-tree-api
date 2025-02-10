from django.contrib import admin
from .models import Profile, Relative, FamilyRelation, OfflineRelative, BondRequestNotification

admin.site.register(Profile)
admin.site.register(FamilyRelation)
admin.site.register(BondRequestNotification)
admin.site.register(Relative)
admin.site.register(OfflineRelative)
