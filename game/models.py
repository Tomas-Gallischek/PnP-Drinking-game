from django.db import models

class player(models.Model):
    name = models.CharField(max_length=100, blank=True)
    lvl = models.IntegerField(default=1, blank=True)
    xp = models.IntegerField(default=0, blank=True)
    xp_need = models.IntegerField(default=100, blank=True)
    panak = models.IntegerField(default=0, blank=True)
    maly_kelimek = models.IntegerField(default=0, blank=True)
    velky_kelimek = models.IntegerField(default=0, blank=True)

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
            self.xp_need = int(xp_need * 1.2)
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