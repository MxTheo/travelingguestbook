from django.urls import path

from weaktie.views import UserChatActivityAlternativeView, UserChatActivityView

from . import views

urlpatterns = [
    path("<str:username>/", UserChatActivityView.as_view(), name="user-chatactivity"),
    path("<str:username>/2/", UserChatActivityAlternativeView.as_view(), name="user-chatactivity-alternative"),
    path('profiel/<str:username>/', views.UserDetail.as_view(), name='user-profile'),
]
