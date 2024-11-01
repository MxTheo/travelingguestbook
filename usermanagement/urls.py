from django.urls import path
from usermanagement import views

urlpatterns = [
    path("register/", views.Register.as_view(), name="register"),
    path(
        "dashboard/gespreksketting/",
        views.dashboard_logmessage,
        name="dashboard_logmessage",
    ),
    path("dashboard/mijncodes/", views.dashboard_sociable, name="dashboard_sociable"),
    path("profile/<str:username>", views.UserDetail.as_view(), name="profile"),
    path("editaccount/", views.update_profile, name="editaccount"),
]
