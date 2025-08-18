from django.urls import path
from usermanagement import views

urlpatterns = [
    path("register/", views.Register.as_view(), name="register"),

    path("profile/<str:username>", views.UserDetail.as_view(), name="profile"),
    path("editaccount/", views.update_profile, name="editaccount"),
]
