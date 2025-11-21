from django.db import models

class player(models.Model):
    name = models.CharField(max_length=100, blank=True)
    lvl = models.IntegerField(default=0, blank=True)
    xp = models.IntegerField(default=0, blank=True)
    panak = models.IntegerField(default=0, blank=True)
    maly_kelimek = models.IntegerField(default=0, blank=True)
    velky_kelimek = models.IntegerField(default=0, blank=True)
    

    def __str__(self):
        return self.name