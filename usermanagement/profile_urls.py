from django.urls import path

from weaktie.views import UserChatActivityAlternativeView, UserChatActivityView

from . import views

urlpatterns = [
    path('<str:username>/', views.UserDetail.as_view(), name='user-profile'),
    path("chat/<str:username>/", UserChatActivityView.as_view(), name="user-chatactivity"),
    path("chat/<str:username>/2/", UserChatActivityAlternativeView.as_view(), name="user-chatactivity-alternative"),
]
