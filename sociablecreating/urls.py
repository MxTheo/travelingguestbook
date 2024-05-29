from django.urls import path
from . import views

urlpatterns = [
    # CRUD Sociable
    path('create-sociable/', views.SociableCreate.as_view(), name='create-sociable'),
    path('<slug:slug>', views.SociableDetail.as_view(), name='sociable'),
    path('update-sociable/<slug:slug>', views.SociableUpdate.as_view(), name='update-sociable'),
    path('delete-sociable/<slug:slug>', views.SociableDelete.as_view(), name='delete-sociable'),

    path('', views.home, name='home'),

    path('create-logmessage/<slug:slug>', views.LogMessageCreate.as_view(), name='create-logmessage'),
    path('delete-logmessage/<str:pk>', views.LogMessageDelete.as_view(), name='delete-logmessage'),
    
    path('search-sociable/', views.search_sociable, name='search-sociable'),
]
