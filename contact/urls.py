from django.urls import path
from . import views

urlpatterns = [
    path('contact/', views.contact, name='contact'),
    path('success/', views.SuccessView.as_view(), name='success'),
    path('about/', views.about, name='about'),
    path('help/', views.help, name='help'),
]