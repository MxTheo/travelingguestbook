from django.urls import path
from . import views

urlpatterns = [
    path('nieuwecode/', views.create_chatroom, name='create-chatroom'),
    path('verwijdercode/<slug:slug>', views.ChatRoomDelete.as_view(), name='delete-chatroom'),

    path('chat', views.home, name='chat'),

    path('nieuwbericht/<slug:slug>', views.ChatMessageCreate.as_view(), name='create-chatmessage'),
    path('verwijderbericht/<str:pk>', views.ChatMessageDelete.as_view(), name='delete-chatmessage'),

    path('c/<slug:slug>/', views.ChatRoomDetail.as_view(), name='chatroom'),

]
