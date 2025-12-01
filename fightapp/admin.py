from django.contrib import admin

from .models import boss, FightLog, TurnLog, boss_names_descriptions

admin.site.register(boss)
admin.site.register(FightLog)
admin.site.register(TurnLog)
admin.site.register(boss_names_descriptions)