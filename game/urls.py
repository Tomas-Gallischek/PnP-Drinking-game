from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('player_info/<int:player_id>/', views.player_info, name='player_info'),
    path('leaderboard', views.leaderboard, name='leaderboard'),
    path('drink/<int:player_id>/', views.drink, name='drink'),
]