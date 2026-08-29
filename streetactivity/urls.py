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
    path("lossereflecties/", views.ReflectionListViewLoose.as_view(), name="reflection-list-no-activity"),
    path(
        "<int:pk>/reflecties/straatactiviteit/",
        views.ReflectionListViewStreetActivity.as_view(),
        name="reflection-list-activity",
    ),
    path(
        "<int:pk>/reflectie/nieuw/",
        views.ReflectionCreateViewActivity.as_view(),
        name="create-reflection-activity",
    ),
    path(
        "reflectie/nieuw/",
        views.ReflectionCreateViewNoActivity.as_view(),
        name="create-reflection-no-activity",
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
    path(
        "upload-foto/<int:activity_id>/",
        views.StreetActivityPhotoCreateView.as_view(),
        name="create-streetactivity-photo",
    ),
    path(
        'verwijder-foto/<int:pk>',
        views.StreetActivityPhotoDeleteView.as_view(),
        name='delete-streetactivity-photo'),
    path(
        'gallerij/<int:activity_id>/',
        views.StreetActivityPhotoListView.as_view(),
        name='streetactivity-photo-list'),
]
