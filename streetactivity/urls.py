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
    path('<int:activity_id>/references/add/',
         views.ExternalReferenceCreateView.as_view(), 
         name='external_reference_create'),

     path('<int:pk>/swot/add/',
         views.SWOTElementCreateView.as_view(),
         name='create-swotelement'),
     path('<int:pk>/swot/bewerk',
          views.SWOTElementUpdateView.as_view(), name="update-swotelement"),
     path('swot/element/<int:pk>/', 
         views.SWOTElementDetailView.as_view(),
         name='swotelement-detail'),
     path('<int:pk>/swot/', views.SWOTElementListView.as_view(), name='swotelement-list'),
     path('<int:pk>/herken_swotelement', views.recognize_swotelement, name="recognize-swotelement"),
     path('<int:pk>/stem_formulering', views.vote_formulation, name="vote-formulation")
]
