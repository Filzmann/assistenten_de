from datetime import timedelta
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from assistenten.functions.calendar_functions import check_feiertag, get_duration, get_ersten_xxtag
from assistenten.models import Adresse, Urlaub, AU, FesteSchicht, AbstractCalendarEntry
from assistenten.models.assistent import Assistent
from assistenten.models.assistenznehmer import ASN

from django.utils import timezone
from django.utils.datetime_safe import datetime, time, date


class Schicht(AbstractCalendarEntry):
    asn = models.ForeignKey(ASN, on_delete=models.CASCADE)
    ist_kurzfristig = models.BooleanField(default=0)
    ist_ausfallgeld = models.BooleanField(default=0)
    ist_assistententreffen = models.BooleanField(default=0)
    ist_pcg = models.BooleanField(default=0)
    ist_schulung = models.BooleanField(default=0)
    beginn_adresse = models.ForeignKey(Adresse, on_delete=models.CASCADE, related_name='+')
    ende_adresse = models.ForeignKey(Adresse, on_delete=models.CASCADE, related_name='+')

    @property
    def lohn(self):
        return self.assistent.lohn(self.beginn).grundlohn

    @property
    def nachtzuschlag(self):
        return float(self.assistent.lohn(self.beginn).nacht_zuschlag) * self.nachtstunden

    @property
    def orgazulage(self):
        return float(self.assistent.lohn(self.beginn).orga_zuschlag) * self.stunden

    @property
    def wechselzulage(self):
        return float(self.assistent.lohn(self.beginn).wechselschicht_zuschlag) * self.stunden

    @property
    def kurzfristig(self):
        lohn = self.assistent.lohn(self.beginn)
        return float(lohn.grundlohn) * float(self.stunden) * (
                float(lohn.kurzfristig_zuschlag_prozent) / 100) if self.ist_kurzfristig else None

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
                              'add_info': '13:00 - 21:00 Uhr',
                              }

        if feiertagsstunden > 0:
            grund_formatiert = feiertagsarray['zuschlagsgrund'].lower().replace('.', '').replace(' ', '_')
            spaltenname = grund_formatiert + '_zuschlag'
            stundenzuschlag = float(getattr(self.assistent.lohn(self.beginn), spaltenname))
            schichtzuschlag = feiertagsarray['stunden_gesamt'] * stundenzuschlag
            feiertagsarray['text'] = feiertagsarray['zuschlagsgrund'] + ': ' + "{:,.2f}".format(
                feiertagsarray['stunden_gesamt']
            ) + ' Std = ' + "{:,.2f}€".format(schichtzuschlag)
            return feiertagsarray
        return None

    def get_year_of_biggest_part(self):
        teilschichten = self.split_by_null_uhr()
        maxschicht = None
        max_duration = 0
        for teilschicht in teilschichten:
            dauer = get_duration(teilschicht.beginn, teilschicht.ende, 'hours')
            if dauer > max_duration:
                max_duration = dauer
                maxschicht = teilschicht
        return maxschicht.beginn.year

    @classmethod
    def add_feste_schichten_in_period(cls,
                                      erster_tag: datetime, letzter_tag: datetime,
                                      assistent: Assistent or bool = False,
                                      asn: ASN or bool = False):
        feste_schichten = FesteSchicht.objects

        if assistent:
            feste_schichten = feste_schichten.filter(assistent=assistent)

        if asn:
            feste_schichten = feste_schichten.filter(asn=asn)

        for feste_schicht in feste_schichten:

            wtag_int = int(feste_schicht.wochentag) - 1
            erster_xxtag_des_monats = get_ersten_xxtag(wtag_int, erster_tag)
            monat = erster_tag.month
            year = erster_tag.year
            maxday = (letzter_tag - timedelta(days=1)).date()

            schichtbeginn_zeit = feste_schicht.beginn
            schichtende_zeit = feste_schicht.ende

            for woche in range(0, 5):

                tag_zahl = woche * 7 + erster_xxtag_des_monats
                if tag_zahl <= maxday.day:
                    tag_datum = date(
                        year=year,
                        month=monat,
                        day=tag_zahl
                    )
                    if feste_schicht.beginn < feste_schicht.ende:
                        start = timezone.make_aware(datetime.combine(tag_datum, schichtbeginn_zeit))
                        end = timezone.make_aware(datetime.combine(tag_datum, schichtende_zeit))
                    # nachtschicht. es gibt keine regelmäßigen dienstreisen!
                    else:
                        start = timezone.make_aware(datetime.combine(tag_datum, schichtbeginn_zeit))
                        end = timezone.make_aware(datetime.combine(tag_datum + timedelta(days=1),
                                                                   schichtende_zeit))

                    # TODO Sperrzeiten des AS checken

                    if not (AU.is_occupied(beginn=start, ende=end, assistent=feste_schicht.assistent)
                            or Urlaub.is_occupied(beginn=start, ende=end, assistent=feste_schicht.assistent)
                            or Schicht.is_occupied(beginn=start, ende=end, assistent=feste_schicht.assistent, asn=False)
                            or Schicht.is_occupied(beginn=start, ende=end, assistent=False, asn=feste_schicht.asn)):
                        # TODO Sperrzeiten des AS checken
                        home = Adresse.objects.filter(is_home=True).filter(asn=feste_schicht.asn)[0]
                        schicht_neu = Schicht(beginn=start,
                                              ende=end,
                                              asn=feste_schicht.asn,
                                              assistent=feste_schicht.assistent,
                                              beginn_adresse=home,
                                              ende_adresse=home)
                        schicht_neu.save()

    def __repr__(self):
        return f"Schicht( Beginn: {self.beginn!r}, Ende: {self.ende!r}, Stunden: {self.stunden}, Lohn: {self.lohn}, ASN: {self.asn!r}  - AS: {self.assistent})"

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
