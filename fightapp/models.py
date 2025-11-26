from django.db import models






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
