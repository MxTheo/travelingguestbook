from django.urls import path
from usermanagement import views

urlpatterns = [
    path('register/', views.Register.as_view(), name='register'),
    path('bewerk/', views.ProfileUpdateView.as_view(), name='update-account'),
    path("<str:username>/", views.UserDetail.as_view(), name="user"),
]
