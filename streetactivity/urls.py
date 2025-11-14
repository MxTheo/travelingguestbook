from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r"streetactivity", views.StreetActivityViewSet, basename="streetactiviteiten")
router.register(r"experience", views.ExperienceViewSet, basename="momenten")

urlpatterns = [
    path("api/", include(router.urls)),
    path("",
         views.StreetActivityListView.as_view(),
         name="streetactivity-list"),
    path("info/<int:pk>/",
         views.StreetActivityDetailView.as_view(),
         name="streetactivity-detail"),
    path("nieuw/",
         views.StreetActivityCreateView.as_view(),
         name="create-streetactivity"),
    path("update/<int:pk>/",
         views.StreetActivityUpdateView.as_view(),
         name="update-streetactivity"),
    path("delete/<int:pk>/",
         views.StreetActivityDeleteView.as_view(),
         name="delete-streetactivity"),

     path('ervaringen/', views.ExperienceListView.as_view(), name='experience-list'),
     path("<int:pk>/ervaringen/straatactiviteit/",
         views.ExperienceListViewStreetActivity.as_view(),
         name="experience-list-streetactivity"),
     path("<int:pk>/ervaring/nieuw/",
          views.ExperienceCreateView.as_view(),
          name="create-experience"),
     path("<int:pk>/ervaring/nieuw/beoefenaar/",
          views.ExperienceCreateView.as_view(),
          name="create-experience-from-practitioner"),
     path("<int:pk>/ervaring/nieuw/voorbijganger/",
          views.ExperienceCreateView.as_view(),
          name="create-experience-from-passerby"),
]
