from django.db import models
from assistenten.models import Adresse


class Weg(models.Model):
    entfernung = models.DecimalField(decimal_places=4, max_digits=4)
    dauer_in_minuten = models.IntegerField()
    adresse1_id = models.ForeignKey(Adresse, on_delete=models.CASCADE, related_name='+')
    adresse2_id = models.ForeignKey(Adresse, on_delete=models.CASCADE, related_name='+')

    def __repr__(self):
        return f"Adresse1={self.adresse1_id!r}, " \
               f"Adresse2={self.adresse2_id!r})"
