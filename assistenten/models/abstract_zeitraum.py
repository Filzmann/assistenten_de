from datetime import timedelta
from django.db import models
from django.utils import timezone
from django.utils.datetime_safe import datetime, time

from assistenten.functions.calendar_functions import get_duration


class AbstractZeitraum(models.Model):
    beginn = models.DateTimeField()
    ende = models.DateTimeField()

    class Meta:
        abstract = True

    def clone(self):
        """Returns a clone of this instance."""
        clone = self.__class__()
        for f in self.__class__._meta.fields:
            setattr(clone, f.attname, getattr(self, f.attname))
        return clone

    @property
    def stunden(self):
        return get_duration(self.beginn, self.ende, "minutes") / 60

    @property
    def nachtstunden(self):
        """Gibt die Anzahl der Stunden einer Schicht zurück, die vor 6 Uhr und nach 21 Uhr stattfinden"""

        nachtstunden = 0

        null_uhr = timezone.make_aware(datetime.combine(self.beginn.date(), time(0, 0)))
        sechs_uhr = timezone.make_aware(datetime.combine(self.beginn.date(), time(6, 0)))
        einundzwanzig_uhr = timezone.make_aware(datetime.combine(self.beginn.date(), time(21, 0)))

        # Schicht beginnt zwischen 0 und 6 uhr
        if null_uhr <= self.beginn <= sechs_uhr:
            if self.ende <= sechs_uhr:
                # Schicht endet spätestens 6 uhr
                nachtstunden += get_duration(self.beginn, self.ende, 'minutes') / 60

            elif sechs_uhr <= self.ende <= einundzwanzig_uhr:
                # Schicht endet nach 6 uhr aber vor 21 uhr
                nachtstunden += get_duration(self.beginn, sechs_uhr, 'minutes') / 60

            else:
                # schicht beginnt vor 6 uhr und geht über 21 Uhr hinaus
                # das bedeutet ich ziehe von der kompletten schicht einfach die 15 Stunden Tagschicht ab.
                # es bleibt der Nacht-An
                nachtstunden += get_duration(self.beginn, self.ende, 'minutes') / 60 - 15
        # Schicht beginnt zwischen 6 und 21 uhr
        elif sechs_uhr <= self.beginn <= einundzwanzig_uhr:
            # fängt am tag an, geht aber bis in die nachtstunden
            if self.ende > einundzwanzig_uhr:
                nachtstunden += get_duration(einundzwanzig_uhr, self.ende, 'minutes') / 60
        else:
            # schicht beginnt nach 21 uhr - die komplette schicht ist in der nacht
            nachtstunden += get_duration(self.beginn, self.ende, 'minutes') / 60

        return nachtstunden

    def check_mehrtaegig(self):
        # wenn schicht um 0 uhr endet, ist es noch der alte Tag
        if self.ende.hour == 0 and self.ende.minute == 0:
            ende = (self.ende - timedelta(days=1)).date()
        else:
            ende = self.ende.date()

        if self.beginn.date() == ende:
            return False
        else:
            return True

    def split_by_null_uhr(self):

        ausgabe = []
        rest = self.clone()
        if not self.ende:
            raise ValueError(f"{__class__} hat kein Ende")
        if not self.beginn:
            raise ValueError(f"{__class__} hat keinen Beginn")
        if self.ende < self.beginn:
            raise ValueError(f'ende {self.ende} is before beginn{self.beginn}')
        while rest.check_mehrtaegig() and rest.beginn <= rest.ende:
            out = rest.clone()
            rest.beginn = timezone.make_aware(
                datetime.combine(rest.beginn.date() + timedelta(days=1),
                                 time(0, 0)
                                 )
            )
            out.ende = rest.beginn
            ausgabe.append(out)
        if rest.stunden > 0:
            ausgabe.append(rest)
        return ausgabe



    @classmethod
    def get_by_person_and_date_range_splitted(cls, start, end, assistent=False, asn=False):
        if not end:
            raise ValueError(f"{__class__} hat kein Ende")
        if not start:
            raise ValueError(f"{__class__} hat keinen Beginn")
        if end < start:
            raise ValueError(f'end {end} is before start{start}')

        schichten = \
            cls.objects.filter(beginn__range=(start, end)) | \
            cls.objects.filter(ende__range=(start, end))

        if assistent:
            schichten = schichten.filter(assistent=assistent)

        if asn:
            schichten = schichten.filter(asn=asn)

        sliced_schichten = []
        for schicht in schichten:
            ergebnisse = schicht.split_by_null_uhr()
            sliced_schichten.extend(ergebnisse)

        return cls.clean_shifts_in_period(sliced_schichten, start, end)

    @staticmethod
    def clean_shifts_in_period(schichts: list, start: datetime, end: datetime):
        for schicht in schichts:
            if schicht.beginn >= end or schicht.ende <= start:
                schichts.remove(schicht)
        return schichts

    def __str__(self):
        return f"Zeitraum: {self.beginn} - {self.ende}"


