from django.urls import path
from . import views

urlpatterns = [
    path("",
         views.StreetActivityListView.as_view(),
         name="streetactivity_list"),
    path("info/<int:pk>/",
         views.StreetActivityDetailView.as_view(),
         name="streetactivity_detail"),
    path("nieuw/",
         views.StreetActivityCreateView.as_view(),
         name="create-streetactivity"),
    path("update/<int:pk>/",
         views.StreetActivityUpdateView.as_view(),
         name="update-streetactivity"),
    path("delete/<int:pk>/",
         views.StreetActivityDeleteView.as_view(),
         name="delete-streetactivity"),
]
