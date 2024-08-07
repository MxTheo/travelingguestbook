from django.urls import path
from . import views

urlpatterns = [
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    path('help/', views.helppage, name='help'),
]
