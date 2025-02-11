from django.contrib import admin
from .models import Profile, OnlineRelative, FamilyRelation, OfflineRelative, BondRequestNotification

admin.site.register(Profile)
admin.site.register(FamilyRelation)
admin.site.register(BondRequestNotification)
admin.site.register(OnlineRelative)
admin.site.register(OfflineRelative)
