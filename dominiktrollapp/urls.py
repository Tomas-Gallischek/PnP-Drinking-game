from django.urls import path
from . import views

urlpatterns = [
    path('', views.dominik_troll, name='dominiktroll'),
    path('vez/', views.vez, name='vez'),
]