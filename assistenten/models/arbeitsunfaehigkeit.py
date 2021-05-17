from django.db import models

from assistenten.models import Assistent


class AU(models.Model):
    assistent = models.ForeignKey(Assistent, on_delete=models.CASCADE)
    beginn = models.DateField()
    ende = models.DateField()

