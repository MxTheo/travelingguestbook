from django.urls import path
from usermanagement import views

urlpatterns = [
    path('register/', views.Register.as_view(), name='register'),
    path("<str:username>/", views.UserDetail.as_view(), name="user"),
]
