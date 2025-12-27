from django.contrib import admin
from django.urls import path, include
from . import settings
from django.conf.urls.static import static



# DODĚLAT URLS !!!!

urlpatterns = [
    path('', include('game.urls',)),
    path('admin/', include('dominiktrollapp.urls')),
    path('admin22/', admin.site.urls),
    path('tutorialapp/', include('tutorialapp.urls')),
    path('fightapp/', include('fightapp.urls')),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)