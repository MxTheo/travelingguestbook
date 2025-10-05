from django.urls import path
from . import views

urlpatterns = [
    path("straatactiviteiten", views.StreetActivityListView.as_view(), name="streetactivity_list"),
    path("straatactiviteit/<int:pk>/", views.StreetActivityDetailView.as_view(), name="streetactivity_detail"),
    path("straatactiviteit/nieuw/", views.StreetActivityCreateView.as_view(), name="create-streetactivity"),
    path("straatactiviteit/<int:pk>/update/", views.StreetActivityUpdateView.as_view(), name="update-streetactivity"),
    path("straatactiviteit/<int:pk>/delete/", views.StreetActivityDeleteView.as_view(), name="delete-streetactivity"),
]