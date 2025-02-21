from django.urls import path
from . import views

app_name = "families"
urlpatterns = [
    path("create/", views.create_family, name="create_family"),
    path("<uuid:family_id>/", views.view_family, name="view_family"),
    path("<uuid:family_id>/update/", views.update_family, name="update_family"),

    path("handler/add/", views.add_handler, name="add_handler"),
    path("handler/<uuid:handler_id>/delete/", views.delete_handler, name="delete_handler"),
    
    path("<uuid:family_id>/origin/add/", views.add_origin, name="add_origin"),
    path("<uuid:family_id>/origin/update/", views.update_origin, name="update_origin"),

    path("<uuid:family_id>/house-info/add/", views.add_house_info, name="add_house_info"),
    path("<uuid:family_id>/house-info/update/", views.update_house_info, name="update_house_info"),

    path("<uuid:family_id>/belief-system/add/", views.add_belief_system, name="add_belief_system"),
    path("<uuid:family_id>/belief-system/update/", views.update_belief_system, name="update_belief_system"),

    path("<uuid:family_id>/other-info/add/", views.add_other_information, name="add_other_info"),
    path("<uuid:family_id>/other-info/update/", views.update_other_information, name="update_other_information"),

    path("<uuid:family_id>/eulogy/add/", views.add_eulogy, name="add_eulogy"),
    path("<uuid:family_id>/eulogy/update/", views.update_eulogy, name="update_eulogy"),

    path("<uuid:family_id>/family-head/add/", views.add_family_head, name="add_family_head"),
    path("<uuid:family_id>/family-head/update/", views.update_family_head, name="update_family_head"),
    path("<uuid:family_id>/family-head/<uuid:family_head_id>/delete/", views.update_family_head, name="update_family_head"),

]