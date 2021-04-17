from django.db import models

from assistenten.models.assistent import Assistent
from assistenten.models.assistenznehmer import ASN


class FesteSchicht(models.Model):
    assistent = models.ForeignKey(Assistent, on_delete=models.CASCADE)
    asn = models.ForeignKey(ASN, on_delete=models.CASCADE)

    # extra Data
    wochentag = models.CharField(max_length=10)
    beginn = models.TimeField()
    ende = models.TimeField()



    def __repr__(self):
        return f"Feste Schicht({self.wochentag!r}, {self.beginn!r} - {self.ende!r})"
