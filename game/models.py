from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
import random

class pocet_hracu(models.Model):
    pocet_hracu_now = models.IntegerField(default=1)
    pocet_hracu_full = models.IntegerField(default=1)
    pocet_hracu_off = models.IntegerField(default=1)

    all_players_dmg = models.IntegerField(default=1, blank=True)
    all_players_armor = models.IntegerField(default=1, blank=True)
    all_player_hp = models.IntegerField(default=1, blank=True)


    def all_stats_counter(self):
        all_players = player.objects.all()
        all_dmg = 0
        all_armor = 0
        all_hp = 0
        for one in all_players:
            all_dmg += one.dmg_now 
            all_armor += one.armor_now
            all_hp += one.hp_now
        self.all_players_dmg = all_dmg
        self.all_players_armor = all_armor
        self.all_players_hp = all_hp
        self.save()
    
    # ZAPLATIT SI COPILOTA

    def __str__(self):
        return str(self.pocet_hracu_now)

class player(models.Model):
    active = models.BooleanField(default=False)
    name = models.CharField(max_length=100, blank=True)
    lvl = models.IntegerField(default=1, blank=True)
    xp = models.IntegerField(default=0, blank=True)
    xp_need = models.IntegerField(default=50, blank=True)
    score = models.IntegerField(default=0, blank=True)
    energie = models.IntegerField(default=100, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)])

    panak = models.IntegerField(default=0, blank=True)
    maly_kelimek = models.IntegerField(default=0, blank=True)
    velky_kelimek = models.IntegerField(default=0, blank=True)


    povolani = models.CharField(max_length=50, blank=True, default='nic')

    dmg = models.IntegerField(blank=True, default= 1)
    dmg_koef = models.FloatField(blank=True, default= 1)
    dmg_now = models.FloatField(blank=True, default= 1)

    armor = models.IntegerField(blank=True, default= 1)
    armor_koef = models.FloatField(blank=True, default= 1)
    armor_now = models.FloatField(blank=True, default= 1)

    hp = models.IntegerField(blank=True, default=1)
    hp_koef = models.FloatField(blank=True, default=1)
    hp_now = models.FloatField(blank=True, default=1)
    hp_actual_fight = models.IntegerField(blank=True, default=1)


    # Uvnitř class player(models.Model):
    def add_xp(self, amount):
        self.xp += amount
        self.lvl_up() 


    def lvl_up(self):
        xp = self.xp
        xp_need = self.xp_need
        if xp >= xp_need:
            xp -= xp_need
            self.xp = xp
            self.lvl += 1
            self.xp_need = int(xp_need * 1.1)
            self.save()

            # Díky tomuto bude definitivní koeficient náhodný při každém levelupu  (rozmezí 50%)
            random_dmg = random.uniform(0.5, 1.5)
            random_armor = random.uniform(0.5, 1.5)
            random_hp = random.uniform(0.5, 1.5)

            print(f"Random dmg koef: {self.dmg_koef}, Random armor koef: {self.armor_koef}, Random hp koef: {self.hp_koef}")
            print(f"Random dmg: {random_dmg}, Random armor: {random_armor}, Random hp: {random_hp}")

            self.dmg_now += round(self.dmg + ((self.dmg_koef * random_dmg) * self.lvl))
            self.armor_now += round(self.armor + ((self.armor_koef * random_armor) * self.lvl))
            self.hp_now += round(self.hp + ((self.hp_koef * random_hp) * self.lvl))
            self.hp_actual_fight = self.hp_now
            self.save()

    def score_counter(self):
        stats = achievements.objects.get(player=self)
        self.score = stats.total_dmg_delt + stats.total_dmg_taken
        self.save()


    def __str__(self):
        return self.name


# VEDLEJŠÍ ÚKOLY přímo navázané na hráče
class side_quest(models.Model):

    rarity_choices = [
        ('common', 'Common'),
        ('uncommon', 'Uncommon'),
        ('rare', 'Rare'),
        ('epic', 'Epic'),
        ('legendary', 'Legendary'),
    ]
    player = models.ForeignKey(player, on_delete=models.CASCADE, related_name='side_quests')
    quest_name = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    xp_reward = models.IntegerField(default=0, blank=True)
    rarity = models.CharField(max_length=50, blank=True, choices=rarity_choices)
    done = models.BooleanField(default=False, blank=True)
    advisor = models.CharField(max_length=100, blank=True)


    def __str__(self):
        return self.quest_name

# MOŽNOSTI ÚKOLŮ
class side_quest_databese(models.Model):

    rarity_choices = [
        ('common', 'Common'),
        ('uncommon', 'Uncommon'),
        ('rare', 'Rare'),
        ('epic', 'Epic'),
        ('legendary', 'Legendary'),
    ]
    quest_name = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    xp_reward = models.IntegerField(default=0, blank=True)
    rarity = models.CharField(max_length=50, blank=True, choices=rarity_choices)


    def __str__(self):
        return self.quest_name
    

class achievements(models.Model):
    player = models.ForeignKey(player, on_delete=models.CASCADE, related_name='achievements')
    total_dmg_delt = models.IntegerField(default=0, blank=True)
    best_dmg_delt = models.IntegerField(default=0, blank=True)
    total_dmg_taken = models.IntegerField(default=0, blank=True)


    def __str__(self):
        return f'Achievements of {self.player.name}'
    
class jmena_hracu(models.Model):
    name = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name