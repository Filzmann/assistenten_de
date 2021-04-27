from django.db import models

from assistenten.models import Adresse
from assistenten.models.assistent import Assistent
from assistenten.models.assistenznehmer import ASN


class Schicht(models.Model):
    beginn = models.DateTimeField()
    ende = models.DateTimeField()
    asn = models.ForeignKey(ASN, on_delete=models.CASCADE)
    assistent = models.ForeignKey(Assistent, on_delete=models.CASCADE)
    ist_kurzfristig = models.BooleanField()
    ist_ausfallgeld = models.BooleanField()
    ist_assistententreffen = models.BooleanField()
    ist_pcg = models.BooleanField()
    ist_schulung = models.BooleanField()
    beginn_adresse = models.ForeignKey(Adresse, on_delete=models.CASCADE, related_name='+')
    ende_adresse = models.ForeignKey(Adresse, on_delete=models.CASCADE, related_name='+')

    def __repr__(self):
        return f"Schicht( Beginn: {self.beginn!r}, Ende: {self.ende!r}, ASN: {self.asn!r})"

    def __str__(self):
        return f"Schicht({self.beginn} - {self.ende} - ASN: {self.asn} - AS: {self.assistent}"

