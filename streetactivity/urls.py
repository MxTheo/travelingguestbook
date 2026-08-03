from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(
    r"streetactivity", views.StreetActivityViewSet, basename="straatactiviteiten"
)
router.register(r"reflection", views.ReflectionViewSet, basename="reflecties")

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
    path("reflecties/", views.ReflectionListView.as_view(), name="reflection-list"),
    path(
        "<int:pk>/reflecties/straatspel/",
        views.ReflectionListViewStreetActivity.as_view(),
        name="reflection-list-streetactivity",
    ),
    path(
        "<int:pk>/reflectie/nieuw/",
        views.ReflectionCreateView.as_view(),
        name="create-reflection",
    ),
    path(
        "verwijder/reflectie/<int:pk>",
        views.ReflectionDeleteView.as_view(),
        name="delete-reflection",
    ),
    path(
        "bewerk/reflectie/<int:pk>",
        views.ReflectionUpdateView.as_view(),
        name="update-reflection",
    ),
]
