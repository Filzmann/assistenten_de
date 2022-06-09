from django.db import models

from assistenten.models.assistent import Assistent


class Brutto(models.Model):

    monat = models.DateTimeField()
    bruttolohn = models.DecimalField(decimal_places=2, max_digits=6)
    stunden_gesamt = models.DecimalField(decimal_places=2, max_digits=5)
    assistent = models.ForeignKey(Assistent, on_delete=models.CASCADE)

    @classmethod
    def new_or_update(cls, brutto, stunden, monat, assistent):
        # check, ob für diesen monat vorhanden
        updatebrutto = cls.objects.filter(monat=monat)
        if updatebrutto:
            updatebrutto[0].bruttolohn = brutto
            updatebrutto[0].stunden_gesamt = stunden
            updatebrutto[0].save()
        else:
            insertbrutto = cls(
                monat=monat,
                bruttolohn=brutto,
                stunden_gesamt=stunden,
                assistent=assistent
            )
            insertbrutto.save()


    def __repr__(self):
        return f" {self.monat} {self.bruttolohn} {self.stunden_gesamt}"
