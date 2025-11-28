from django.contrib import admin

from .models import boss, FightLog, TurnLog

admin.site.register(boss)
admin.site.register(FightLog)
admin.site.register(TurnLog)