from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('adedamola/', admin.site.urls),
    path('v1/authentication/', include('authentication.urls')),
    path('v1/profiles/', include('profiles.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)