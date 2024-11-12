from django.urls import path
from .views import ObservationFormView
from . import views

urlpatterns = [
    path('stap1-observatie/', ObservationFormView.as_view(), name='step1-observation'),
    path('stap2-observatie/', views.prepare_for_choice_of_observations_step_2, name='step2-observation'),
]