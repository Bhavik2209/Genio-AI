from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('', views.index, name='index'),
    path('content-generation/', views.home, name='home'),
    path('generate/', csrf_exempt(views.generate), name='generate'),
]