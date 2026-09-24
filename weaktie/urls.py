from django.urls import path

from . import views

urlpatterns = [
    path('nieuw/', views.WhereaboutCreateView.as_view(), name='create-get-together'),
    path('bewerk/<int:pk>', views.WhereaboutUpdateView.as_view(), name='update-get-together' ),
    path('verwijder/<int:pk>', views.WhereaboutDeleteView.as_view(), name='delete-get-together' ),
]
