from django.db import models

class player(models.Model):
    name = models.CharField(max_length=100)
    lvl = models.IntegerField(default=0)
    xp = models.IntegerField(default=0)
    

    def __str__(self):
        return self.name