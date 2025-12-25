from turtle import position
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
import random
from colorama import init, Fore, Style
from django.utils import timezone


class pocet_hracu(models.Model):
    pocet_hracu_now = models.IntegerField(default=1)
    pocet_hracu_full = models.IntegerField(default=1)
    pocet_hracu_off = models.IntegerField(default=1)

    all_players_dmg = models.IntegerField(default=1, blank=True)
    all_players_armor = models.IntegerField(default=1, blank=True)
    all_player_hp = models.IntegerField(default=1, blank=True)

    all_dmg_delt = models.IntegerField(default=0, blank=True)
    all_dmg_taken = models.IntegerField(default=0, blank=True)
    all_death_counter = models.IntegerField(default=0, blank=True)
    all_best_dmg = models.IntegerField(default=0, blank=True)

    all_score_dmg_delt = models.IntegerField(default=0, blank=True)
    all_score_dmg_taken = models.IntegerField(default=0, blank=True)
    all_score_death_counter = models.IntegerField(default=0, blank=True)
    all_score_best_dmg = models.IntegerField(default=0, blank=True)
    all_score = models.IntegerField(default=0, blank=True)


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
        self.all_player_hp = all_hp

        self.all_dmg_delt = 0
        self.all_dmg_taken = 0
        self.all_death_counter = 0
        self.all_best_dmg = 0
        self.all_score_dmg_delt = 0
        self.all_score_dmg_taken = 0
        self.all_score_death_counter = 0
        self.all_score_best_dmg = 0
        self.all_score = 0

        for one in all_players:
            stats = achievements.objects.get(player=one)
            self.all_dmg_delt += stats.total_dmg_delt    
            self.all_dmg_taken += stats.total_dmg_taken
            self.all_death_counter += stats.death_counter
            self.all_best_dmg += stats.best_dmg_delt #Abych následně mohl pracovat s procenty
            self.all_score_dmg_delt += one.score_dmg_delt
            self.all_score_dmg_taken += one.score_dmg_taken
            self.all_score_death_counter += one.score_death_counter
            self.all_score_best_dmg += one.score_best_dmg
            self.all_score += one.score

            self.save()

        self.save()


    def __str__(self):
        return str(self.pocet_hracu_now)

class player(models.Model):
    profile_img = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    role_img_id = models.IntegerField(blank=True, null=True) # 1 = mág, 2 = hunter, 3 = warrior
    gender = models.CharField(max_length=10, blank=True, null=True)

    active = models.BooleanField(default=False)
    name = models.CharField(max_length=100, blank=True)
    lvl = models.IntegerField(default=1, blank=True)
    xp = models.IntegerField(default=0, blank=True)
    xp_need = models.IntegerField(default=50, blank=True)
    
    score_dmg_delt = models.IntegerField(default=0, blank=True)
    score_dmg_taken = models.IntegerField(default=0, blank=True)
    score_death_counter = models.IntegerField(default=0, blank=True)
    score_best_dmg = models.IntegerField(default=0, blank=True)
    score = models.IntegerField(default=0, blank=True)

    quest_refresh = models.IntegerField(default=1)
    energie = models.IntegerField(default=200, blank=True, validators=[MinValueValidator(0), MaxValueValidator(200)])
    last_energy_update = models.DateTimeField(default=timezone.now)
    skill_points = models.IntegerField(default=0, blank=True)

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

    critic_chance = models.FloatField(default=1, blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(50)])  # šance na kritický zásah
    dodge_chance = models.FloatField(default=1, blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(50)])
    
    def energy_change(self):
        if self.energie <= 200:
            time_now = timezone.now()
            time_diff = time_now - self.last_energy_update
            minutes_passed = round(time_diff.total_seconds() // 60)
            energy_to_add = int(round(minutes_passed * 5))
            if self.energie + energy_to_add >= 200:
                self.energie = 200
            elif self.energie + energy_to_add <= 0:
                self.energie = 0
            else:
                self.energie += energy_to_add
            self.last_energy_update = time_now
            self.save()


    # Uvnitř class player(models.Model):
    def add_xp(self, amount):
        self.xp += amount
        self.save()
        self.lvl_up() 


    def lvl_up(self):
        xp = self.xp
        xp_need = self.xp_need
        if xp >= xp_need:
            xp -= xp_need
            self.xp = xp
            self.lvl += 1
            self.xp_need = int(round((xp_need + 40)))

            print(Fore.LIGHTCYAN_EX + f"{self.name} level up to {self.lvl}!" + Style.RESET_ALL)

    # ABY SE POSTAVY VYLEPŠOVALY I LEVELEM TROCHU
            if self.povolani == 'mag':
                self.hp_now += round(self.hp_koef / 3)
                self.dmg_now += round(self.dmg_koef / 3)
                self.armor_now += round(self.armor_koef / 3)
            elif self.povolani == 'hunter':
                self.hp_now += round(self.hp_koef / 3)
                self.dmg_now += round(self.dmg_koef / 3)
                self.armor_now += round(self.armor_koef / 3)
            elif self.povolani == 'valecnik':
                self.hp_now += round(self.hp_koef / 3)
                self.dmg_now += round(self.dmg_koef / 3)
                self.armor_now += round(self.armor_koef / 3)

            self.skill_points += 3

            if self.povolani == 'mag':
                critic_koef = 2
                dodge_koef = 1
            elif self.povolani == 'hunter':
                critic_koef = 1.5
                dodge_koef = 1.5
            elif self.povolani == 'valecnik':
                critic_koef = 1
                dodge_koef = 2

            self.critic_chance = self.lvl * critic_koef
            self.dodge_chance = self.lvl * dodge_koef
            self.save()
            
            self.lvl_up()  # Rekurzivní volání pro případ, že hráč získal více úrovní najednou


    def score_counter(self):
        stats = achievements.objects.get(player=self)
        pocet_hracu_instance = pocet_hracu.objects.first()

        all_delt = pocet_hracu_instance.all_dmg_delt
        all_taken = pocet_hracu_instance.all_dmg_taken
        all_deaths = pocet_hracu_instance.all_death_counter
        all_best = pocet_hracu_instance.all_best_dmg

        # Pomocná funkce pro bezpečné dělení a výpočet podílu z 1000
        def get_share(value, total):
            if total <= 0: return 0
            return round((value / total) * 1000)

        score_dmg_delt = 800 + (get_share(stats.total_dmg_delt, all_delt))
        score_dmg_taken = 800 + (get_share(stats.total_dmg_taken, all_taken))
        score_best_dmg = 800 + (get_share(stats.best_dmg_delt, all_best))
        
        # SPECIÁLNÍ LOGIKA PRO ÚMRTÍ (Nepřímá úměra)
        # Spočítáme podíl na úmrtích a odečteme ho od 1000
        death_share = get_share(stats.death_counter, all_deaths)
        score_death_counter = 1000 - death_share 

        # Teď už všechno jen sčítáme
        self.score = score_dmg_delt + score_dmg_taken + score_best_dmg + score_death_counter
        
        self.score_dmg_delt = score_dmg_delt
        self.score_dmg_taken = score_dmg_taken
        self.score_death_counter = score_death_counter
        self.score_best_dmg = score_best_dmg
        self.save()


# VEDLEJŠÍ ÚKOLY přímo navázané na hráče
class side_quest(models.Model):

    rarity_choices = [
        ('common', 'Common'),
        ('uncommon', 'Uncommon'),
        ('rare', 'Rare'),
        ('epic', 'Epic'),
        ('legendary', 'Legendary'),
    ]

    quest_type_choices = [
    ('alko', 'Alko'),
    ('nealko', 'Nealko'),
    ('coop', 'Coop')
    ]
    player = models.ForeignKey(player, on_delete=models.CASCADE, related_name='side_quests')
    player_name = models.CharField(max_length=100, blank=True)
    player_coop = models.CharField(max_length=100, blank=True)
    coop_player_name = models.CharField(max_length=100, blank=True)
    quest_type = models.CharField(max_length=100, blank=True, choices=quest_type_choices)
    quest_name = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    xp_reward = models.IntegerField(default=0, blank=True)
    rarity = models.CharField(max_length=50, blank=True, choices=rarity_choices)
    done = models.BooleanField(default=False, blank=True)


    def __str__(self):
        return f"{self.quest_name} - {self.player.name} + {self.player_coop}"

# MOŽNOSTI ÚKOLŮ
class side_quest_databese(models.Model):

    quest_type_choices = [
        ('alko', 'Alko'),
        ('nealko', 'Nealko'),
        ('coop', 'Coop')
    ]

    quest_name = models.CharField(max_length=100, blank=True)
    quest_type = models.CharField(max_length=100, blank=True, choices=quest_type_choices)
    description = models.TextField(blank=True)



class side_quest_generated(models.Model):

    rarity_choices = [
        ('common', 'Common'),
        ('uncommon', 'Uncommon'),
        ('rare', 'Rare'),
        ('epic', 'Epic'),
        ('legendary', 'Legendary'),
    ]

    quest_type_choices = [
        ('alko', 'Alko'),
        ('nealko', 'Nealko'),
        ('coop', 'Coop')
    ]
    player = models.ForeignKey(player, on_delete=models.CASCADE, related_name='side_quests_generated', null=True, blank=True)
    quest_name = models.CharField(max_length=100, blank=True)
    quest_type = models.CharField(max_length=100, blank=True, choices=quest_type_choices)
    description = models.TextField(blank=True)
    xp_reward = models.IntegerField(default=0, blank=True)
    rarity = models.CharField(max_length=50, blank=True, choices=rarity_choices)
    

    def __str__(self):
        return f"{self.quest_name} ({self.quest_type})"
    

class achievements(models.Model):
    player = models.ForeignKey(player, on_delete=models.CASCADE, related_name='achievements')
    total_dmg_delt = models.IntegerField(default=0, blank=True)
    best_dmg_delt = models.IntegerField(default=0, blank=True)
    total_dmg_taken = models.IntegerField(default=0, blank=True)
    death_counter = models.IntegerField(default=0, blank=True)
    attack_counter = models.IntegerField(default=0, blank=True)
    attack_get = models.IntegerField(default=0, blank=True)

    panaky = models.IntegerField(default=0, blank=True)
    maly_kelimek = models.IntegerField(default=0, blank=True)
    velky_kelimek = models.IntegerField(default=0, blank=True)


    def __str__(self):
        return f'Achievements of {self.player.name}'
    
class jmena_hracu(models.Model):
    name = models.CharField(max_length=100, blank=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    player_profile_img = models.ImageField(upload_to='profile_images/', blank=True, null=True)


    def __str__(self):
        return self.name
    

class test_model(models.Model):
    test_status = models.BooleanField(default=False)