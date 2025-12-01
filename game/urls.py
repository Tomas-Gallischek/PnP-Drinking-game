from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('player_info/<int:player_id>/', views.player_info, name='player_info'),
    path('leaderboard', views.leaderboard, name='leaderboard'),
    path('drink/<int:player_id>/', views.drink, name='drink'),
    path('sidequest/', views.sidequest, name='sidequest'),
    path('take_quest', views.take_quest, name='take_quest'),
    path('quest_failed', views.quest_failed, name='quest_failed'),
    path('nastenka', views.nastenka, name='nastenka'),
    path('quest_done', views.quest_done, name='quest_done'),
    path('reset', views.reset, name='reset'),
    path('test', views.test, name='test'),
]