from django.contrib import admin
from .models import player, side_quest, side_quest_databese


class SideQuestInline(admin.TabularInline):
    model = side_quest
    extra = 0
    verbose_name_plural = 'Vedlejší úkoly'

class PlayerAdmin(admin.ModelAdmin):
    inlines = [SideQuestInline]
    list_display = ('name', 'lvl', 'xp', 'xp_need', 'panak', 'maly_kelimek', 'velky_kelimek')
    search_fields = ('name',)
    ordering = ('-xp',)


    
admin.site.register(player, PlayerAdmin) 
admin.site.register(side_quest)
admin.site.register(side_quest_databese)