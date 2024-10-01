from django.urls import path
from usermanagement import views

urlpatterns = [
    path('register/', views.Register.as_view(), name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/<str:username>', views.UserDetail.as_view(), name='profile'),
    path('editaccount/', views.update_profile, name='editaccount'),

    path('resetdescription/', views.reset_custom_description_for_code, name='resetdescription'),
]
