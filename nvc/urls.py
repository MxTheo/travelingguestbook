from django.urls import path
from .views import ObservationFormView

urlpatterns = [
    path('stap1-observatie/', ObservationFormView.as_view(), name='step1-observation'),
]