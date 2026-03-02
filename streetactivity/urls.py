from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(
    r"streetactivity", views.StreetActivityViewSet, basename="straatactiviteiten"
)
router.register(r"word", views.WordViewSet, basename="worden")

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
    path("woorden/", views.WordListView.as_view(), name="word-list"),
    path(
        "<int:pk>/woorden/straatspel/",
        views.WordListViewStreetActivity.as_view(),
        name="word-list-streetactivity",
    ),
    path(
        "<int:pk>/woord/nieuw/",
        views.WordCreateView.as_view(),
        name="create-word",
    ),
    path(
        "verwijder/woord/<int:pk>",
        views.WordDeleteView.as_view(),
        name="delete-word",
    ),
    path(
        "bewerk/woord/<int:pk>",
        views.WordUpdateView.as_view(),
        name="update-word",
    ),
    path(
        "woordenboom",
        views.WordTreeView.as_view(),
        name="wordtree",
    )
]
