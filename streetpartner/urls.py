from django.urls import path
from . import views

urlpatterns = [
    path('verzoekstraatpartner/<str:username>', views.SendPartnershipRequestView.as_view(), name='request_partnership'),
]
