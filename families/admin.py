from django.contrib import admin
from .models import Family, FamilyHead, Handler, Origin, HouseInfo, BeliefSystem, OtherInformation, Eulogy

admin.site.register(Family)
admin.site.register(Handler)
admin.site.register(Origin)
admin.site.register(HouseInfo)
admin.site.register(BeliefSystem)
admin.site.register(OtherInformation)
admin.site.register(Eulogy)
admin.site.register(FamilyHead)
