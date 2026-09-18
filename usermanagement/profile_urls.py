from django.urls import path

from usermanagement import views

urlpatterns = [
    path("<str:username>/", views.UserDetail.as_view(), name="user"),
]
