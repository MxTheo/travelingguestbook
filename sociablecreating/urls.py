from django.urls import path
from . import views

urlpatterns = [
    # CRUD Sociable
    path('nieuwecode/', views.create_sociable, name='create-sociable'),
    # path('edit/<slug:slug>', views.SociableUpdate.as_view(), name='update-sociable'),
    path('<slug:slug>', views.SociableDetail.as_view(), name='sociable'),
    path('verwijdercode/<slug:slug>', views.SociableDelete.as_view(), name='delete-sociable'),

    path('', views.home, name='home'),

    path('nieuwbericht/<slug:slug>', views.LogMessageCreate.as_view(), name='create-logmessage'),
    path('verwijderbericht/<str:pk>', views.LogMessageDelete.as_view(), name='delete-logmessage'),
    path('bewerkbericht/<str:pk>', views.LogMessageUpdate.as_view(), name='update-logmessage'),

    path('berichtvoorjou/', views.search_sociable, name='search-sociable'),
    path('message-read/<str:pk>', views.display_code_after_message_is_read, name='message-read'),
]
