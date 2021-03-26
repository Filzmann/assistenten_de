from django.db import models

from assistenten.models.assistent import Assistent


class Brutto(models.Model):

    monat = models.DateTimeField()
    bruttolohn = models.DecimalField(decimal_places=2, max_digits=6)
    stunden_gesamt = models.DecimalField(decimal_places=2, max_digits=5)
    assistent = models.ForeignKey(Assistent, on_delete=models.CASCADE)

    def __repr__(self):
        return f" {self.monat} {self.bruttolohn} {self.stunden_gesamt}"
