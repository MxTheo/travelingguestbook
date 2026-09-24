from django.urls import path

from . import views

urlpatterns = [
    path('nieuw/', views.WhereaboutCreateView.as_view(), name='create-whereabout'),
    path('bewerk/<int:pk>', views.WhereaboutUpdateView.as_view(), name='update-whereabout' ),
    path('verwijder/<int:pk>', views.WhereaboutDeleteView.as_view(), name='delete-whereabout' ),
]
