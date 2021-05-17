from django.db import models
from assistenten.models.assistent import Assistent


class Urlaub(models.Model):
    assistent = models.ForeignKey(Assistent, on_delete=models.CASCADE)
    beginn = models.DateField()
    ende = models.DateField()
    status = models.CharField(max_length=10)

    def __repr__(self):
        return f"Urlaub({self.beginn!r}, " \
               f"-{self.ende!r}) "

    def __str__(self):
        return f"Urlaub({self.beginn!r}, " \
               f"-{self.ende!r}) "
