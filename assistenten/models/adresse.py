from django.db import models

from assistenten.models import Assistent, ASN


class Adresse(models.Model):
    bezeichner = models.CharField(max_length=30)
    strasse = models.CharField(max_length=30)
    hausnummer = models.CharField(max_length=8)
    plz = models.CharField(max_length=5)
    stadt = models.CharField(max_length=30)

    assistent = models.ForeignKey(Assistent, on_delete=models.CASCADE)
    asn = models.ForeignKey(ASN, on_delete=models.CASCADE)

    def __repr__(self):
        return f"Address(id={self.bezeichner!r}, " \
               f"strasse={self.strasse!r}, " \
               f"hausnummer={self.hausnummer!r}, " \
               f"plz={self.plz!r})"

    def __str__(self):
        return f"{self.strasse} {self.hausnummer}, {self.plz} {self.stadt}"
