from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('overons/', views.AboutView.as_view(), name='about'),
    path('help/', views.HelpView.as_view(), name='help'),
]