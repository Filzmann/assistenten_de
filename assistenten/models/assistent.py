from django.db import models

from assistenten.models import ASN


class Assistent(models.Model):
    name = models.CharField(max_length=30)
    vorname = models.CharField(max_length=30)
    email = models.CharField(max_length=30)
    einstellungsdatum = models.DateTimeField()

    asn = models.ManyToManyField(ASN, through='AssociationAsAsn')

    def __repr__(self):
        return f"Assistent({self.name!r}, {self.vorname!r})"
