from django.db import models
from assistenten.models.assistent import Assistent


class Urlaub(models.Model):
    assistent = models.ForeignKey(Assistent, on_delete=models.CASCADE)
    beginn = models.DateTimeField()
    ende = models.DateTimeField()
    status = models.CharField(max_length=10)
