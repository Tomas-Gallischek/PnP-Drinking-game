from django.contrib import admin
from .models import player, pocet_hracu, side_quest, side_quest_databese, achievements


class SideQuestInline(admin.TabularInline):
    model = side_quest
    extra = 0
    verbose_name_plural = 'Vedlejší úkoly'

class AchievementsInline(admin.TabularInline):
    model = achievements
    extra = 0
    verbose_name_plural = 'Úspěchy hráče'

class PlayerAdmin(admin.ModelAdmin):
    inlines = [SideQuestInline, AchievementsInline]
    list_display = ('name', 'lvl', 'xp', 'xp_need', 'panak', 'maly_kelimek', 'velky_kelimek')
    search_fields = ('name',)
    ordering = ('-xp',)


    
admin.site.register(player, PlayerAdmin) 
admin.site.register(pocet_hracu)
admin.site.register(side_quest)
admin.site.register(side_quest_databese)
admin.site.register(achievements)
# Register your models here.
