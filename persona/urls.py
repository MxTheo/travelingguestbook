from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'persona', views.PersonaViewSet, basename='personas')
router.register(r'problem', views.ProblemViewSet, basename='problem')
router.register(r'reaction', views.ReactionViewSet, basename='reaction')

urlpatterns = [
    path('api/', include(router.urls)),
    path('', views.PersonaListView.as_view(), name='persona-list'),
    path('nieuw/', views.PersonaCreateView.as_view(), name='create-persona'),
    path('<int:pk>/', views.PersonaDetailView.as_view(), name='persona-detail'),
    path('<int:pk>/bewerk/', views.PersonaUpdateView.as_view(), name='update-persona'),
    path('<int:persona_pk>/problemen/nieuw/', views.ProblemCreateView.as_view(), name='create-problem'),
    path('<int:persona_pk>/reacties/nieuw/', views.ReactionCreateView.as_view(), name='create-reaction'),
    path('problemen/<int:pk>/verwijder/', views.ProblemDeleteView.as_view(), name='delete-problem'),
    path('reacties/<int:pk>/verwijder/', views.ReactionDeleteView.as_view(), name='delete-reaction'),
]
