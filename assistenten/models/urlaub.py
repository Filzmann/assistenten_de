from django.db import models
from assistenten.models import AbstractZeitraum
from assistenten.models.assistent import Assistent


class Urlaub(AbstractZeitraum):
    assistent = models.ForeignKey(Assistent, on_delete=models.CASCADE)
    status = models.CharField(max_length=10)

    def __repr__(self):
        return f"Urlaub({self.beginn!r}, " \
               f"-{self.ende!r}) "

    def __str__(self):
        return f"Urlaub({self.beginn!r}, " \
               f"-{self.ende!r}) "



