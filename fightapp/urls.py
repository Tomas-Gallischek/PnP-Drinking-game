from django.urls import path
from . import views

urlpatterns = [
    path('', views.dungeon, name='dungeon'),
    path('fight/', views.fight, name='fight'),

]