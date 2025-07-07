from django.urls import path
from . import views

urlpatterns = [
    path("", views.oogcontact_home, name="oogcontact_home"),
    path("aanmelden/", views.RegistrationCreateView.as_view(), name="registration_create"),
    path("aanmelding/<int:pk>/", views.RegistrationDetailView.as_view(), name="registration_detail"),
]
