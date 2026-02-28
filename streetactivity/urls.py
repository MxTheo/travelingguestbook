from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(
    r"streetactivity", views.StreetActivityViewSet, basename="straatactiviteiten"
)
router.register(r"moment", views.MomentViewSet, basename="momenten")

urlpatterns = [
    path("api/", include(router.urls)),
    path("", views.StreetActivityListView.as_view(), name="streetactivity-list"),
    path(
        "info/<int:pk>/",
        views.StreetActivityDetailView.as_view(),
        name="streetactivity-detail",
    ),
    path(
        "nieuw/", views.StreetActivityCreateView.as_view(), name="create-streetactivity"
    ),
    path(
        "update/<int:pk>/",
        views.StreetActivityUpdateView.as_view(),
        name="update-streetactivity",
    ),
    path(
        "delete/<int:pk>/",
        views.StreetActivityDeleteView.as_view(),
        name="delete-streetactivity",
    ),
    path("momenten/", views.MomentListView.as_view(), name="moment-list"),
    path(
        "<int:pk>/momenten/straatspel/",
        views.MomentListViewStreetActivity.as_view(),
        name="moment-list-streetactivity",
    ),
    path(
        "<int:pk>/moment/nieuw/",
        views.MomentCreateView.as_view(),
        name="create-moment",
    ),
    path(
        "verwijder/moment/<int:pk>",
        views.MomentDeleteView.as_view(),
        name="delete-moment",
    ),
    path(
        "bewerk/moment/<int:pk>",
        views.MomentUpdateView.as_view(),
        name="update-moment",
    ),
]
