from django.urls import path
from usermanagement import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
]
