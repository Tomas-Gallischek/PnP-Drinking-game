from django.db import models
from game.models import player


class boss(models.Model):
    name = models.CharField(max_length=100)
    patro = models.IntegerField(default=1)
    description = models.TextField(blank=True)
    defeated = models.BooleanField(default=False)

    lvl = models.IntegerField(default=1)

    dmg = models.IntegerField(default=1)
    armor = models.IntegerField(default=1)
    hp = models.IntegerField(default=10)

    reward_xp = models.IntegerField(default=10)

    def __str__(self):
        return self.name

class FightLog(models.Model):
    """Log celého souboje."""
    
    # Základní informace o boji
    fight_time = models.DateTimeField(auto_now_add=True)
    boss = models.ForeignKey(boss, on_delete=models.CASCADE, related_name='fight_logs')
    player_count = models.IntegerField(verbose_name="Počet aktivních hráčů")
    
    # Výsledek
    outcome_choices = [
        ('players', 'Hráči zvítězili'),
        ('boss', 'Boss zvítězil'),
        ('draw', 'Remíza (nepravděpodobné)')
    ]
    outcome = models.CharField(max_length=10, choices=outcome_choices, default='draw')
    
    # Statistika
    total_damage_dealt_by_players = models.IntegerField(default=0)
    total_damage_received_by_players = models.IntegerField(default=0)
    final_boss_hp = models.IntegerField(verbose_name="Konečné HP Bosse", default=0)
    
    def __str__(self):
        return f"Souboj s {self.boss.name} - {self.outcome} ({self.fight_time.strftime('%Y-%m-%d %H:%M')})"

class TurnLog(models.Model):
    """Detailní log jednoho tahu/útoku."""
    
    fight = models.ForeignKey(FightLog, on_delete=models.CASCADE, related_name='turn_logs')
    turn_number = models.IntegerField()
    
    # Kdo útočil
    attacker_is_boss = models.BooleanField(default=False)
    attacker_player = models.ForeignKey(player, on_delete=models.SET_NULL, null=True, blank=True, related_name='attack_turns')
    
    # Kdo byl cílem
    target_player = models.ForeignKey(player, on_delete=models.SET_NULL, null=True, blank=True, related_name='target_turns')
    
    # Parametry tahu
    damage_dealt = models.IntegerField(verbose_name="Udělené poškození")
    attacker_damage_roll = models.IntegerField(verbose_name="Základní hod útočníka před brněním")
    target_armor_roll = models.IntegerField(verbose_name="Hod brnění cíle")
    
    # Stavy po tahu
    boss_hp_after = models.IntegerField(verbose_name="HP Bosse po tahu")
    target_player_hp_after = models.IntegerField(null=True, blank=True, verbose_name="HP Hráče po tahu")

    def __str__(self):
        return f"Tah {self.turn_number} v boji {self.fight_id}"






