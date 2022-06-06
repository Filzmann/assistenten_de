from datetime import timedelta
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from assistenten.functions.calendar_functions import check_feiertag, get_duration
from assistenten.models import Adresse, Urlaub, AU
from assistenten.models.abstract_zeitraum import AbstractZeitraum
from assistenten.models.assistent import Assistent
from assistenten.models.assistenznehmer import ASN

from django.utils import timezone
from django.utils.datetime_safe import datetime, time


class Schicht(AbstractZeitraum):
    asn = models.ForeignKey(ASN, on_delete=models.CASCADE)
    assistent = models.ForeignKey(Assistent, on_delete=models.CASCADE)
    ist_kurzfristig = models.BooleanField(default=0)
    ist_ausfallgeld = models.BooleanField(default=0)
    ist_assistententreffen = models.BooleanField(default=0)
    ist_pcg = models.BooleanField(default=0)
    ist_schulung = models.BooleanField(default=0)
    beginn_adresse = models.ForeignKey(Adresse, on_delete=models.CASCADE, related_name='+')
    ende_adresse = models.ForeignKey(Adresse, on_delete=models.CASCADE, related_name='+')

    @property
    def lohn(self):
        return self.assistent.lohn(self.beginn)

    @property
    def zuschlaege(self):
        feiertagsstunden = 0
        feiertagsstunden_steuerfrei = 0
        feiertagsstunden_steuerpflichtig = 0
        feiertagsarray = {}
        zuschlagsgrund = ''

        anfang = self.beginn
        ende = self.ende

        heute_null_uhr = timezone.make_aware(datetime.combine(self.beginn.date(), time(0, 0)))
        hl_abend = timezone.make_aware(datetime(anfang.year, 12, 24))
        silvester = timezone.make_aware(datetime(anfang.year, 12, 31))
        sechsuhr = timezone.make_aware(datetime(anfang.year, anfang.month, anfang.day, 6, 0, 0))
        dreizehn_uhr = timezone.make_aware(datetime(anfang.year, anfang.month, anfang.day, 13, 0, 0))
        vierzehn_uhr = timezone.make_aware(datetime(anfang.year, anfang.month, anfang.day, 14, 0, 0))
        einundzwanzig_uhr = timezone.make_aware(datetime(anfang.year, anfang.month, anfang.day, 21, 0, 0))

        if check_feiertag(anfang) != '':
            feiertagsstunden = self.stunden

            feiertagsarray = {'zuschlagsgrund': 'Feiertag',
                              'stunden_gesamt': feiertagsstunden,
                              'stunden_steuerfrei': feiertagsstunden,
                              'stunden_steuerpflichtig': 0,
                              'add_info': check_feiertag(anfang)
                              }

        elif heute_null_uhr == hl_abend or heute_null_uhr == silvester:
            if heute_null_uhr == hl_abend:
                zuschlagsgrund = 'Hl. Abend'
            if heute_null_uhr == silvester:
                zuschlagsgrund = 'Silvester'

            if anfang < sechsuhr:
                if ende <= sechsuhr:
                    feiertagsstunden_steuerfrei = feiertagsstunden_steuerpflichtig = 0
                elif sechsuhr < ende <= vierzehn_uhr:
                    feiertagsstunden_steuerpflichtig = get_duration(ende, sechsuhr, 'hours')
                    feiertagsstunden_steuerfrei = 0
                elif vierzehn_uhr < ende:
                    feiertagsstunden_steuerpflichtig = 8
                    feiertagsstunden_steuerfrei = get_duration(vierzehn_uhr, ende, 'hours')
            elif sechsuhr <= anfang:
                if ende <= vierzehn_uhr:
                    feiertagsstunden_steuerpflichtig = get_duration(ende, anfang, 'hours')
                    feiertagsstunden_steuerfrei = 0
                elif vierzehn_uhr < ende:
                    feiertagsstunden_steuerpflichtig = get_duration(anfang, vierzehn_uhr, 'hours')
                    feiertagsstunden_steuerfrei = get_duration(vierzehn_uhr, ende, 'hours')

            feiertagsstunden = feiertagsstunden_steuerfrei + feiertagsstunden_steuerpflichtig
            feiertagsarray = {'zuschlagsgrund': zuschlagsgrund,
                              'stunden_gesamt': feiertagsstunden,
                              'stunden_steuerfrei': feiertagsstunden_steuerfrei,
                              'stunden_steuerpflichtig': feiertagsstunden_steuerpflichtig,
                              'add_info': '13:00 - 21:00 Uhr'
                              }
        elif anfang.weekday() == 6:
            feiertagsstunden = self.stunden
            feiertagsarray = {'zuschlagsgrund': 'Sonntag',
                              'stunden_gesamt': feiertagsstunden,
                              'stunden_steuerfrei': feiertagsstunden,
                              'stunden_steuerpflichtig': 0,
                              'add_info': ''
                              }
        elif anfang.weekday() == 5:
            if anfang < dreizehn_uhr:
                if ende < dreizehn_uhr:
                    feiertagsstunden = 0
                elif dreizehn_uhr < ende <= einundzwanzig_uhr:
                    feiertagsstunden = get_duration(dreizehn_uhr, ende, 'hours')
                else:  # ende > einundzwanzig_uhr:
                    feiertagsstunden = 8  # 21 - 13
            elif dreizehn_uhr <= anfang < einundzwanzig_uhr:
                if ende < einundzwanzig_uhr:
                    feiertagsstunden = self.stunden
                elif ende > einundzwanzig_uhr:
                    feiertagsstunden = get_duration(anfang, einundzwanzig_uhr, 'hours')
            else:
                feiertagsstunden = 0

            feiertagsarray = {'zuschlagsgrund': 'Samstag',
                              'stunden_gesamt': feiertagsstunden,
                              'stunden_steuerfrei': 0,
                              'stunden_steuerpflichtig': feiertagsstunden,
                              'add_info': '13:00 - 21:00 Uhr'
                              }

        return feiertagsarray

    def __repr__(self):
        return f"Schicht( Beginn: {self.beginn!r}, Ende: {self.ende!r}, ASN: {self.asn!r}  - AS: {self.assistent})"

    def __str__(self):
        return f"Schicht({self.beginn} - {self.ende} - ASN: {self.asn} - AS: {self.assistent}"




# Lösche Schicht, wenn Urlaub gespeichert wird.
def delete_schicht_by_signal(sender, instance, created, **kwargs):
    # DELETE-query
    anfang = timezone.make_aware(datetime.combine(instance.beginn, time(0, 0)))
    ende = timezone.make_aware(datetime.combine(instance.ende + timedelta(days=1), time(0, 0)))
    Schicht.objects.filter(
        beginn__range=(anfang, ende)
    ).filter(
        assistent=instance.assistent
    ).delete() | Schicht.objects.filter(
        ende__range=(anfang, ende)
    ).filter(assistent=instance.assistent).delete()


@receiver(post_save, sender=Urlaub)
def delete_urlaubsschicht(sender, instance, created, **kwargs):
    delete_schicht_by_signal(sender, instance, created, **kwargs)


# Lösche Schicht, wenn AU gespeichert wird.
@receiver(post_save, sender=AU)
def delete_urlaubsschicht(sender, instance, created, **kwargs):
    delete_schicht_by_signal(sender, instance, created, **kwargs)
