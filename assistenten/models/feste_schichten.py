from django.db import models

from assistenten.models.assistent import Assistent
from assistenten.models.assistenznehmer import ASN
from assistenten_de.settings import WTAGE


class FesteSchicht(models.Model):
    assistent = models.ForeignKey(Assistent, on_delete=models.CASCADE)
    asn = models.ForeignKey(ASN, on_delete=models.CASCADE)

    # extra Data
    wochentag = models.CharField(max_length=10)
    beginn = models.TimeField()
    ende = models.TimeField()

    @classmethod
    def get_list(cls, asn=None, assistent=None):
        # alle festen Schichten des asn
        feste_schichten_liste = []
        feste_schichten = cls.objects

        if asn:
            feste_schichten = feste_schichten.filter(asn=asn.id)
        if assistent:
            feste_schichten = feste_schichten.filter(assistent=assistent.id)

        for feste_schicht in feste_schichten:
            feste_schichten_liste.append({
                'id': feste_schicht.id,
                'wochentag': WTAGE[feste_schicht.wochentag],
                'beginn': feste_schicht.beginn.strftime("%H:%M"),
                'ende': feste_schicht.ende.strftime("%H:%M"),
            })
        return feste_schichten_liste


    def __repr__(self):
        return f"Feste Schicht({self.wochentag!r}, {self.beginn!r} - {self.ende!r} asn: {self.asn!r} as: {self.assistent!r} )"

    def __str__(self):
        return f"Feste Schicht({self.wochentag!r}, {self.beginn!r} - {self.ende!r} asn: {self.asn!r} as: {self.assistent!r} )"
