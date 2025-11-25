from django.urls import path
from . import views

urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('tut_zazvonit/', views.tut_zazvonit, name='tut_zazvonit'),
    path('tut_odloz_si/', views.tut_odloz_si, name='tut_odloz_si'),
    path('tut_seznameni/', views.tut_seznameni, name='tut_seznameni'),
    path('vyber_postavy/', views.vyber_postavy, name='vyber_postavy'),
    path('vyber_povolani/', views.vyber_povolani, name='vyber_povolani'),
    path('tut_end/', views.tut_end, name='tut_end'),

]