from django.contrib.auth.models import User
from django.db import models
from django.db.models import BooleanField

from assistenten.models import ASN, Assistent


class Sperrzeit(models.Model):
    assistent = models.ForeignKey(Assistent, on_delete=models.CASCADE, null=True, blank=True)
    asn = models.ForeignKey(ASN, on_delete=models.CASCADE, null=True, blank=True)
    beginn = models.DateTimeField()
    ende = models.DateTimeField()

    def __repr__(self):
        return f"Sperrzeit({self.beginn!r}, " \
               f"-{self.ende!r}) "

    def __str__(self):
        return f"Sperrzeit({self.beginn!r}, " \
               f"-{self.ende!r}) "


class FesteSperrzeit(models.Model):
    assistent = models.ForeignKey(Assistent, on_delete=models.CASCADE, null=True, blank=True)
    asn = models.ForeignKey(ASN, on_delete=models.CASCADE, null=True, blank=True)
    wochentag = models.IntegerField()
    beginn = models.TimeField()
    ende = models.TimeField()

    def __repr__(self):
        return f"feste Sperrzeit({self.wochentag!r}, " \
               f"{self.beginn!r} " \
               f"-{self.ende!r}) "

    def __str__(self):
        return f"{self.wochentag!r}, " \
               f"feste Sperrzeit({self.beginn!r} " \
               f"-{self.ende!r}) "
