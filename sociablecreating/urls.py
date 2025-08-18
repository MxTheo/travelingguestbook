from django.urls import path
from . import views

urlpatterns = [
    path('nieuwecode/', views.create_sociable, name='create-sociable'),
    path('verwijdercode/<slug:slug>', views.SociableDelete.as_view(), name='delete-sociable'),

    path('chat', views.home, name='chat'),

    path('nieuwbericht/<slug:slug>', views.LogMessageCreate.as_view(), name='create-logmessage'),
    path('verwijderbericht/<str:pk>', views.LogMessageDelete.as_view(), name='delete-logmessage'),
    path('bewerkbericht/<str:pk>', views.LogMessageUpdate.as_view(), name='update-logmessage'),

    path('c/<slug:slug>/', views.SociableDetail.as_view(), name='sociable'),

]
