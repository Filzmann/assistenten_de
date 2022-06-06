from datetime import timedelta
from django.utils import timezone
from django.utils.datetime_safe import datetime
from django.db.models import Q
from assistenten.models import FesteSchicht, Schicht, Adresse, Brutto, AU, Urlaub
from assistenten.functions.calendar_functions import get_ersten_xxtag, get_duration



def get_feste_schichten(asn=None, assistent=None):
    # alle festen Schichten des asn
    feste_schichten_liste = []
    feste_schichten = FesteSchicht.objects

    if asn:
        feste_schichten = feste_schichten.filter(asn=asn.id)
    if assistent:
        feste_schichten = feste_schichten.filter(assistent=assistent.id)

    wtage = {'1': 'Mo', '2': 'Di', '3': 'Mi', '4': 'Do', '5': 'Fr', '6': 'Sa', '7': 'So'}

    for feste_schicht in feste_schichten:
        feste_schichten_liste.append({
            'id': feste_schicht.id,
            'wochentag': wtage[feste_schicht.wochentag],
            'beginn': feste_schicht.beginn.strftime("%H:%M"),
            'ende': feste_schicht.ende.strftime("%H:%M"),
        })
    return feste_schichten_liste


def add_feste_schichten_asn(erster_tag, letzter_tag, asn):
    add_feste_schichten(erster_tag=erster_tag, letzter_tag=letzter_tag, asn=asn, assistent=None)


def add_feste_schichten_as(erster_tag, letzter_tag, assistent):
    add_feste_schichten(erster_tag=erster_tag, letzter_tag=letzter_tag, assistent=assistent, asn=None)


def add_feste_schichten(erster_tag, letzter_tag, assistent=None, asn=None):
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
        maxday = (letzter_tag - timedelta(days=1)).day

        for woche in range(0, 5):
            tag = woche * 7 + erster_xxtag_des_monats
            if tag <= maxday:
                if feste_schicht.beginn < feste_schicht.ende:
                    start = timezone.make_aware(datetime(year=year,
                                                         month=monat,
                                                         day=tag,
                                                         hour=feste_schicht.beginn.hour,
                                                         minute=feste_schicht.beginn.minute))
                    end = timezone.make_aware(datetime(year=year,
                                                       month=monat,
                                                       day=tag,
                                                       hour=feste_schicht.ende.hour,
                                                       minute=feste_schicht.ende.minute))
                # nachtschicht. es gibt keine regelmäßigen dienstreisen!
                else:
                    start = timezone.make_aware(datetime(year=year,
                                                         month=monat,
                                                         day=tag,
                                                         hour=feste_schicht.beginn.hour,
                                                         minute=feste_schicht.beginn.minute))
                    end = timezone.make_aware(datetime(year=year,
                                                       month=monat,
                                                       day=tag,
                                                       hour=feste_schicht.ende.hour,
                                                       minute=feste_schicht.ende.minute) + timedelta(days=1))

                # TODO Sperrzeiten des AS checken

                if not (check_au(datum=start, assistent=feste_schicht.assistent)
                        or check_urlaub(datum=start, assistent=feste_schicht.assistent)
                        or check_au(datum=end - timedelta(minutes=1), assistent=feste_schicht.assistent)
                        or check_urlaub(datum=end - timedelta(minutes=1), assistent=assistent)
                        or check_schicht(beginn=start, ende=end, assistent=feste_schicht.assistent, asn=False)
                        or check_schicht(beginn=start, ende=end, assistent=False, asn=feste_schicht.asn)):
                    # TODO Sperrzeiten des AS checken
                    home = Adresse.objects.filter(is_home=True).filter(asn=feste_schicht.asn)[0]
                    schicht_neu = Schicht(beginn=start,
                                          ende=end,
                                          asn=feste_schicht.asn,
                                          assistent=feste_schicht.assistent,
                                          beginn_adresse=home,
                                          ende_adresse=home)
                    schicht_neu.save()


def get_schicht_hauptanteil(schicht):
    # TODO: Reisebegleitungen/mehrtägig
    teilschichten = schicht.split_by_null_uhr()
    maxschicht = None
    max_duration = 0
    for teilschicht in teilschichten:
        dauer = get_duration(teilschicht.beginn, teilschicht.ende, 'hours')
        if dauer > max_duration:
            max_duration = dauer
            maxschicht = teilschicht
    return maxschicht.beginn







def brutto_in_db(brutto, stunden, monat, assistent):
    # check, ob für diesen monat vorhanden
    updatebrutto = Brutto.objects.filter(monat=monat)
    if updatebrutto:
        updatebrutto[0].bruttolohn = brutto
        updatebrutto[0].stunden_gesamt = stunden
        updatebrutto[0].save()
    else:
        insertbrutto = Brutto(
            monat=monat,
            bruttolohn=brutto,
            stunden_gesamt=stunden,
            assistent=assistent
        )
        insertbrutto.save()


def check_au(datum, assistent):
    if AU.objects.filter(beginn__lte=datum).filter(ende__gte=datum).filter(assistent=assistent).count():
        return True
    else:
        return False


def check_urlaub(datum, assistent):
    if Urlaub.objects.filter(beginn__lte=datum).filter(ende__gte=datum).filter(assistent=assistent).count():
        return True
    else:
        return False


def check_schicht(beginn, ende, assistent=False, asn=False, speak=False):
    """prüft, ob an einem gegebenen Datum eine Schicht ist.
    wenn speak = true gibt es mehrer print-Ausgaben zur Analyse"""
    # anfang eine minute später und ende eine minute früher, um den Schichtwechsel zu vermeiden

    beginn = beginn + timedelta(minutes=1)
    ende = ende - timedelta(minutes=1)
    if speak:
        print('---' + str(beginn))
        print('---' + str(ende))
        print('---' + str(assistent))
        print('---' + str(asn))
        # print('---------------------------------')
    # alle schichten, die "heute" anfangen, heute enden oder vor heute anfangen und nach heute enden.
    # Q-Notation importiert zur übersichtlichen und kurzen Darstellung von "und" (&) und "oder" (|)
    schichten = Schicht.objects.filter(
        Q(beginn__range=(beginn, ende)) | Q(ende__range=(beginn, ende)) | Q(Q(beginn__lte=beginn) & Q(ende__gte=ende))
    )

    if assistent:
        if speak:
            print('---vor AS + ASN ---')
            print(assistent)
            print(asn)
            print(schichten)
        schichten = schichten.filter(assistent=assistent)

    if asn:
        if speak:
            print('---vor ASN ---')
            print(asn)
            print(schichten)
        schichten = schichten.filter(asn=asn)

    if speak:
        print('---nach AS + ASN ---')
        print(schichten)
    if schichten:
        return True
    return False



def sort_schicht_data_by_beginn(schichten: list):
    """sortiert die schichten an einem tag (in Form einer Liste von dicts von strings)
    nach ihrem beginn"""
    return sorted(schichten, key=lambda j: j['von'])
