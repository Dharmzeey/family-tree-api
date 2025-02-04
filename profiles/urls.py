from django.urls import path
from . import views

app_name = "profiles"
urlpatterns = [
    path("create/", views.create_profile, name="create_profile"),
    path("view/", views.view_profile, name="view_profile"),
    path("update/", views.edit_profile, name="edit_profile"),

    # relatives
    path("relations/", views.get_relations, name="get_relations"),
    path("relatives/search/", views.search_relatives, name="search_relatives"),
    path("relation/create/", views.create_relation, name="create_relation"),
    path("relatives/", views.view_relatives, name="view_relatives"),
    path("offline-relatives/", views.add_offline_relative, name="add_offline_relative"),
]
