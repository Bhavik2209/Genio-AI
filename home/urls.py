from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('content-generation/', views.home, name='home'),
    path('generate/', views.generate, name='generate'),
    path('check-task/<str:task_id>/', views.check_task_status, name='check_task_status'),
]