from datetime import datetime, timedelta
from django.db import models
from django.db.models import Q
from django.utils import timezone
from assistenten.models import Assistent, AbstractZeitraum, Brutto, ASN


class AbstractCalendarEntry(AbstractZeitraum):
    class Meta:
        abstract = True

    assistent = models.ForeignKey(Assistent, on_delete=models.CASCADE)

    @property
    def stunden(self):
        return self.berechne_urlaub_au_saetze()['stunden_pro_tag']

    @property
    def lohn(self):
        return self.berechne_urlaub_au_saetze()['pro_stunde']

    def berechne_urlaub_au_saetze(self):
        datum = self.beginn
        akt_monat = timezone.make_aware(datetime(year=datum.year, month=datum.month, day=1))
        for zaehler in range(1, 7):
            vormonat_letzter = akt_monat - timedelta(days=1)
            akt_monat = timezone.make_aware(datetime(year=vormonat_letzter.year, month=vormonat_letzter.month, day=1))
        startmonat = akt_monat
        endmonat = timezone.make_aware(datetime(year=datum.year, month=datum.month, day=1))

        bruttosumme = 0
        stundensumme = 0
        zaehler = 0

        bruttoloehne = Brutto.objects.filter(
            monat__range=(startmonat, endmonat)).filter(
            assistent=self.assistent
        )

        for brutto in bruttoloehne:
            bruttosumme += brutto.bruttolohn
            stundensumme += brutto.stunden_gesamt
            zaehler += 1
        if zaehler == 0 or stundensumme == 0:
            return {
                'stunden_pro_tag': 1,
                'pro_stunde': 5
            }
        return {
            'stunden_pro_tag': float((stundensumme / zaehler) / 30),
            'pro_stunde': float(bruttosumme / stundensumme)
        }

    @classmethod
    def is_occupied(cls, beginn: datetime,
                    ende: datetime,
                    assistent: Assistent or bool = False,
                    asn: ASN or bool = False):
        # anfang eine minute später und ende eine Sekunde früher, um den Schichtwechsel zu vermeiden

        beginn = beginn + timedelta(seconds=1)
        ende = ende - timedelta(seconds=1)

        # alle schichten, die "heute" anfangen, heute enden oder vor heute anfangen und nach heute enden.
        # Q-Notation importiert zur übersichtlichen und kurzen Darstellung von "und" (&) und "oder" (|)
        schichten = cls.objects.filter(
            Q(beginn__range=(beginn, ende)) | Q(ende__range=(beginn, ende)) | Q(
                Q(beginn__lte=beginn) & Q(ende__gte=ende))
        )
        if assistent:
            schichten = schichten.filter(assistent=assistent)

        if asn:
            schichten = schichten.filter(asn=asn)

        if schichten:
            return True
        return False


class AU(AbstractCalendarEntry):
    def __str__(self):
        return f"AU {self.assistent}: {self.beginn} - {self.ende} "
