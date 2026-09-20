from django.urls import path

from . import views

urlpatterns = [
    path('nieuw/', views.GetTogetherCreateView.as_view(), name='create-get-together'),
    path('bewerk/<int:pk>', views.GetTogetherUpdateView.as_view(), name='update-get-together' ),
    path('verwijder/<int:pk>', views.GetTogetherDeleteView.as_view(), name='delete-get-together' ),
]
