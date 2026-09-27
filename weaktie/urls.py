from django.urls import path

from . import views

urlpatterns = [
    path('gelegenheid/nieuw/', views.WhereaboutCreateView.as_view(), name='create-whereabout'),
    path('gelegenheid/bewerk/<int:pk>', views.WhereaboutUpdateView.as_view(), name='update-whereabout' ),
    path('gelegenheid/verwijder/<int:pk>', views.WhereaboutDeleteView.as_view(), name='delete-whereabout' ),
    path('link/nieuw/', views.LinkCreateView.as_view(), name='create-link'),
    path('link/verwijder/<int:pk>', views.LinkDeleteView.as_view(), name='delete-link' ),
]
