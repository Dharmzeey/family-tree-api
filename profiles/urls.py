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

    path("bond-notifications/", views.view_bond_requests, name="view_bond_requests"),
    path("process-bond-notifications/", views.process_bond_request, name="process_bond_request"),

    path("relatives/", views.view_relatives, name="view_relatives"),
    path("relatives/<str:relative_id>/", views.view_user_relatives, name="view_user_relatives"),
    path("offline-relatives/", views.add_offline_relative, name="add_offline_relative"),
]
