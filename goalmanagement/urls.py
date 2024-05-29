from django.urls import path
from . import views

urlpatterns = [
    path('create-goal/', views.GoalCreate.as_view(), name='create-goal'),
    path('goals/', views.GoalListView.as_view(), name='goals'),
    path('goal/<str:pk>', views.GoalDetailView.as_view(), name='goal'),
    path('delete-goal/<str:pk>', views.GoalDelete.as_view(), name='delete-goal'),
]
