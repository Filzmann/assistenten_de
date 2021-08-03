from datetime import timedelta

import googlemaps
from django.utils import timezone
from django.utils.datetime_safe import datetime, time
from django.db.models import Q

from assistenten.functions.constants import WTAGE
from assistenten.models import SchichtTemplate, FesteSchicht, Schicht, Adresse, Weg, Brutto, AU, Urlaub, Lohn, \
    Sperrzeit, FesteSperrzeit
from assistenten.functions.calendar_functions import check_feiertag, get_ersten_xxtag, get_duration, shift_month
from assistenten_de.settings import GOOGLE_API_KEY


def get_schicht_templates(asn, order_by=False):
    # alle schicht_templates des asn
    schicht_template_liste = []
    schicht_templates = SchichtTemplate.objects.filter(
        asn=asn.id)
    if order_by:
        schicht_templates = schicht_templates.order_by(order_by)
    for schicht_template in schicht_templates:
        schicht_template_liste.append({
            'id': schicht_template.id,
            'bezeichner': schicht_template.bezeichner,
            'beginn': schicht_template.beginn,
            'ende': schicht_template.ende,
        })

    return schicht_templates


def get_feste_schichten(asn=None, assistent=None):
    # alle festen Schichten des asn
    feste_schichten_liste = []
    feste_schichten = FesteSchicht.objects

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


def split_by_null_uhr_asn(schicht):
    ausgabe = []

    if check_mehrtaegig(schicht):
        rest = dict(start=schicht.beginn, ende=schicht.ende)
        while rest['start'] <= rest['ende']:
            r_start = rest['start']
            neuer_start_rest = timezone.make_aware(datetime(year=r_start.year,
                                                            month=r_start.month,
                                                            day=r_start.day
                                                            )) + timedelta(days=1)

            if neuer_start_rest <= rest['ende']:
                ausgabe.append({'beginn': rest['start'],
                                'ende': neuer_start_rest,
                                'asn': schicht.asn,
                                'assistent': schicht.assistent,
                                'schicht_id': schicht.id,
                                'beginn_adresse': schicht.beginn_adresse,
                                'ende_adresse': schicht.ende_adresse
                                })
            else:
                ausgabe.append({'beginn': rest['start'],
                                'ende': rest['ende'],
                                'asn': schicht.asn,
                                'assistent': schicht.assistent,
                                'schicht_id': schicht.id,
                                'beginn_adresse': schicht.beginn_adresse,
                                'ende_adresse': schicht.ende_adresse
                                })

            rest['start'] = neuer_start_rest
    else:
        ausgabe.append({
            'beginn': schicht.beginn,
            'ende': schicht.ende,
            'asn': schicht.asn,
            'assistent': schicht.assistent,
            'schicht_id': schicht.id,
            'beginn_adresse': schicht.beginn_adresse,
            'ende_adresse': schicht.ende_adresse
        })
    return ausgabe


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
                        or check_schicht(beginn=start, ende=end, assistent=False, asn=feste_schicht.asn)
                        or check_sperrzeit(beginn=start, ende=end, assistent=feste_schicht.assistent, asn=False)
                        or check_sperrzeit(beginn=start, ende=end, assistent=False, asn=feste_schicht.asn)):
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
    teilschichten = split_by_null_uhr_asn(schicht)
    maxschicht = None
    max_duration = 0
    for teilschicht in teilschichten:
        dauer = get_duration(teilschicht['beginn'], teilschicht['ende'], 'hours')
        if dauer > max_duration:
            max_duration = dauer
            maxschicht = teilschicht
    return maxschicht['beginn']


def get_weg_id(adresse1, adresse2):
    # prüfen ob weg in Modell wege vorhanden
    wege = Weg.objects.filter(adresse1=adresse1, adresse2=adresse2) | Weg.objects.filter(adresse1=adresse2,
                                                                                         adresse2=adresse1)
    # print(wege)
    if wege:
        return wege[0].pk
    else:
        weg = make_weg(adresse1, adresse2)
        if weg:
            return weg
        else:
            return False
    # bei bedarf insert, werte für weg + zeit per google api ermitteln


def make_weg(adresse1, adresse2):
    gmaps = googlemaps.Client(key=GOOGLE_API_KEY)

    adresse1_string = \
        adresse1.strasse + ' ' \
        + adresse1.hausnummer + ', ' \
        + adresse1.plz + ' ' \
        + adresse1.stadt

    adresse2_string = \
        adresse2.strasse + ' ' \
        + adresse2.hausnummer + ', ' \
        + adresse2.plz + ' ' \
        + adresse2.stadt

    directions_result = gmaps.directions(adresse1_string,
                                         adresse2_string,
                                         mode="transit",
                                         departure_time=timezone.now())

    if directions_result:
        distance = directions_result[0]['legs'][0]['distance']['value'] / 1000
        duration = round(directions_result[0]['legs'][0]['duration']['value'] / 60 + 0.5)

        weg = Weg(adresse1=adresse1, adresse2=adresse2, entfernung=distance, dauer_in_minuten=duration)
        weg.save()

        return weg.pk
    else:
        return False


def berechne_sa_so_weisil_feiertagszuschlaege(schicht):
    feiertagsstunden = 0
    feiertagsstunden_steuerfrei = 0
    feiertagsstunden_steuerpflichtig = 0
    feiertagsarray = {}
    zuschlagsgrund = ''

    anfang = schicht['beginn']
    ende = schicht['ende']

    if check_feiertag(anfang) != '':
        feiertagsstunden = berechne_stunden(schicht=schicht)

        feiertagsarray = {'zuschlagsgrund': 'Feiertag',
                          'stunden_gesamt': feiertagsstunden,
                          'stunden_steuerfrei': feiertagsstunden,
                          'stunden_steuerpflichtig': 0,
                          'add_info': check_feiertag(anfang)
                          }
    elif timezone.make_aware(datetime(year=anfang.year, month=anfang.month, day=anfang.day)) == \
            timezone.make_aware(datetime(anfang.year, 12, 24)) or \
            timezone.make_aware(datetime(anfang.year, anfang.month, anfang.day)) == \
            timezone.make_aware(datetime(anfang.year, 12, 31)):
        if timezone.make_aware(datetime(anfang.year, anfang.month, anfang.day)) == \
                timezone.make_aware(datetime(anfang.year, 12, 24)):
            zuschlagsgrund = 'Hl. Abend'
        if timezone.make_aware(datetime(anfang.year, anfang.month, anfang.day)) == \
                timezone.make_aware(datetime(anfang.year, 12, 31)):
            zuschlagsgrund = 'Silvester'

        sechsuhr = timezone.make_aware(datetime(anfang.year, anfang.month, anfang.day, 6, 0, 0))
        vierzehn_uhr = timezone.make_aware(datetime(anfang.year, anfang.month, anfang.day, 14, 0, 0))

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
        feiertagsstunden = berechne_stunden(schicht=schicht)
        feiertagsarray = {'zuschlagsgrund': 'Sonntag',
                          'stunden_gesamt': feiertagsstunden,
                          'stunden_steuerfrei': feiertagsstunden,
                          'stunden_steuerpflichtig': 0,
                          'add_info': ''
                          }
    elif anfang.weekday() == 5:
        dreizehn_uhr = timezone.make_aware(datetime(anfang.year, anfang.month, anfang.day, 13, 0, 0))
        einundzwanzig_uhr = timezone.make_aware(datetime(anfang.year, anfang.month, anfang.day, 21, 0, 0))

        if anfang < dreizehn_uhr:
            if ende < dreizehn_uhr:
                feiertagsstunden = 0
            elif dreizehn_uhr < ende <= einundzwanzig_uhr:
                feiertagsstunden = get_duration(dreizehn_uhr, ende, 'hours')
            else:  # ende > einundzwanzig_uhr:
                feiertagsstunden = 8  # 21 - 13
        elif dreizehn_uhr <= anfang < einundzwanzig_uhr:
            if ende < einundzwanzig_uhr:
                feiertagsstunden = berechne_stunden(schicht=schicht)
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


def berechne_stunden(schicht):
    return get_duration(schicht['beginn'], schicht['ende'], "minutes") / 60


def berechne_urlaub_au_saetze(datum, assistent):
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
        assistent=assistent
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


def brutto_in_db(brutto, stunden, monat, assistent):
    # check ob für diesen monat vorhanden
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


def check_mehrtaegig(schicht):
    pseudoende = schicht.ende - timedelta(minutes=2)
    if schicht.beginn.strftime("%Y%m%d") == pseudoende.strftime("%Y%m%d"):
        return 0
    else:
        return 1


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


def check_sperrzeit(beginn, ende, assistent=False, asn=False):
    beginn = beginn + timedelta(minutes=1)
    ende = ende - timedelta(minutes=1)
    # alle schichten, die "heute" anfangen, heute enden oder vor heute anfangen und nach heute enden.
    # Q-Notation importiert zur übersichtlichen und kurzen Darstellung von "und" (&) und "oder" (|)
    sperrzeiten = Sperrzeit.objects.filter(
        Q(beginn__range=(beginn, ende)) | Q(ende__range=(beginn, ende)) | Q(Q(beginn__lte=beginn) & Q(ende__gte=ende))
    )
    if assistent:
        sperrzeiten = sperrzeiten.filter(assistent=assistent)
    if asn:
        sperrzeiten = sperrzeiten.filter(asn=asn)
    if sperrzeiten:
        return True

    sperrzeiten = FesteSperrzeit.objects.filter(
        Q(beginn__range=(beginn, ende)) | Q(ende__range=(beginn, ende)) | Q(Q(beginn__lte=beginn) & Q(ende__gte=ende))
    )
    if assistent:
        sperrzeiten = sperrzeiten.filter(assistent=assistent)
    if asn:
        sperrzeiten = sperrzeiten.filter(asn=asn)
    if sperrzeiten:
        return True

    return False


def check_schicht(beginn, ende, assistent=False, asn=False, speak=False):
    """prüft, ob an einem gegeben Datum eine Schicht ist.
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


def get_erfahrungsstufe(assistent, datum=timezone.now()):
    delta = get_duration(assistent.einstellungsdatum, datum, 'years')
    # einstieg mit 1
    # nach 1 Jahr insgesamt 2
    # nach 3 jahren insgesamt 3
    # nach 6 jahren insg. 4
    # nach 10 Jahren insg. 5
    # nach 15 Jahren insg. 6
    if delta == 0:
        return 1
    elif 1 <= delta < 3:
        return 2
    elif 3 <= delta < 6:
        return 3
    elif 6 <= delta < 10:
        return 4
    elif 10 <= delta < 15:
        return 5
    else:
        return 6


def get_lohn(assistent, datum):
    erfahrungsstufe = get_erfahrungsstufe(assistent=assistent, datum=datum)
    lohn = Lohn.objects.filter(erfahrungsstufe=erfahrungsstufe).filter(
        gueltig_ab__lte=datum).filter(
        eingruppierung=5
    ).order_by('gueltig_ab')[0:1].get()
    if lohn:
        return lohn
    return False


def get_nachtstunden(schicht):
    """Gibt die Anzahl der Stunden einer Schicht zurück, die vor 6 Uhr und nach 21 Uhr stattfinden"""

    nachtstunden = 0

    null_uhr = timezone.make_aware(datetime(year=schicht['beginn'].year,
                                            month=schicht['beginn'].month,
                                            day=schicht['beginn'].day,
                                            hour=0, minute=0, second=0))
    sechs_uhr = timezone.make_aware(datetime(year=schicht['beginn'].year,
                                             month=schicht['beginn'].month,
                                             day=schicht['beginn'].day,
                                             hour=6, minute=0, second=0))
    einundzwanzig_uhr = timezone.make_aware(datetime(year=schicht['beginn'].year,
                                                     month=schicht['beginn'].month,
                                                     day=schicht['beginn'].day,
                                                     hour=21, minute=0, second=0))

    # schicht beginnt zwischen 0 und 6 uhr
    if null_uhr <= schicht['beginn'] <= sechs_uhr:
        if schicht['ende'] <= sechs_uhr:
            # schicht endet spätestens 6 uhr
            nachtstunden += get_duration(schicht['beginn'], schicht['ende'], 'minutes') / 60

        elif sechs_uhr <= schicht['ende'] <= einundzwanzig_uhr:
            # schicht endet nach 6 uhr aber vor 21 uhr
            nachtstunden += get_duration(schicht['beginn'], sechs_uhr, 'minutes') / 60

        else:
            # schicht beginnt vor 6 uhr und geht über 21 Uhr hinaus
            # das bedeutet ich ziehe von der kompletten schicht einfach die 15 Stunden Tagschicht ab.
            # es bleibt der Nacht-An
            nachtstunden += get_duration(schicht['beginn'], schicht['ende'], 'minutes') / 60 - 15
    # schicht beginnt zwischen 6 und 21 uhr
    elif sechs_uhr <= schicht['beginn'] <= einundzwanzig_uhr:
        # fängt am tag an, geht aber bis in die nachtstunden
        if schicht['ende'] > einundzwanzig_uhr:
            nachtstunden += get_duration(einundzwanzig_uhr, schicht['ende'], 'minutes') / 60
    else:
        # schicht beginnt nach 21 uhr - die komplette schicht ist in der nacht
        nachtstunden += get_duration(schicht['beginn'], schicht['ende'], 'minutes') / 60

    return nachtstunden


def get_sliced_schichten_by_as(start, end, assistent):
    """wrapper for get_sliced_schichten"""
    return get_sliced_schichten(start=start, end=end, assistent=assistent)


def get_sliced_schichten_by_asn(start, end, asn):
    """wrapper for get_sliced_schichten"""
    return get_sliced_schichten(start=start, end=end, asn=asn)


def get_sliced_schichten(start, end, assistent=False, asn=False):
    """returns all shifts of specificated as/asn. Splits all nightshifts at midnight"""
    schichten = \
        Schicht.objects.filter(beginn__range=(start, end)) | \
        Schicht.objects.filter(ende__range=(start, end))

    if assistent:
        schichten = schichten.filter(assistent=assistent)

    if asn:
        schichten = schichten.filter(asn=asn)

    sliced_schichten = []
    for schicht in schichten:
        ergebnisse = split_by_null_uhr_asn(schicht)
        for ergebnis in ergebnisse:
            sliced_schichten.append(ergebnis)

    return sliced_schichten


def sort_schicht_data_by_beginn(schichten: list):
    """sortiert die schichten an einem tag (in Form einer Liste von dicts von strings)
    nach ihrem beginn"""
    return sorted(schichten, key=lambda j: j['von'])


def split_by_null_uhr(schicht):
    ausgabe = []

    if check_mehrtaegig(schicht):
        rest = dict(start=schicht.beginn, ende=schicht.ende)
        while rest['start'] <= rest['ende']:
            r_start = rest['start']
            neuer_start_rest = timezone.make_aware(datetime(year=r_start.year,
                                                            month=r_start.month,
                                                            day=r_start.day
                                                            )) + timedelta(days=1)

            if neuer_start_rest <= rest['ende']:
                ausgabe.append({'beginn': rest['start'],
                                'ende': neuer_start_rest,
                                'asn': schicht.asn,
                                'assistent': schicht.assistent,
                                'schicht_id': schicht.id,
                                'ist_assistententreffen': schicht.ist_assistententreffen,
                                'ist_kurzfristig': schicht.ist_kurzfristig,
                                'ist_ausfallgeld': schicht.ist_ausfallgeld,
                                'ist_pcg': schicht.ist_pcg,
                                'ist_schulung': schicht.ist_schulung,
                                'beginn_adresse': schicht.beginn_adresse,
                                'ende_adresse': schicht.ende_adresse
                                })
            else:
                ausgabe.append({'beginn': rest['start'],
                                'ende': rest['ende'],
                                'asn': schicht.asn,
                                'assistent': schicht.assistent,
                                'schicht_id': schicht.id,
                                'ist_assistententreffen': schicht.ist_assistententreffen,
                                'ist_kurzfristig': schicht.ist_kurzfristig,
                                'ist_ausfallgeld': schicht.ist_ausfallgeld,
                                'ist_pcg': schicht.ist_pcg,
                                'ist_schulung': schicht.ist_schulung,
                                'beginn_adresse': schicht.beginn_adresse,
                                'ende_adresse': schicht.ende_adresse
                                })

            rest['start'] = neuer_start_rest
    else:
        ausgabe.append({
            'beginn': schicht.beginn,
            'ende': schicht.ende,
            'asn': schicht.asn,
            'assistent': schicht.assistent,
            'schicht_id': schicht.id,
            'ist_assistententreffen': schicht.ist_assistententreffen,
            'ist_kurzfristig': schicht.ist_kurzfristig,
            'ist_ausfallgeld': schicht.ist_ausfallgeld,
            'ist_pcg': schicht.ist_pcg,
            'ist_schulung': schicht.ist_schulung,
            'beginn_adresse': schicht.beginn_adresse,
            'ende_adresse': schicht.ende_adresse
        })
    return ausgabe


def get_sperrzeiten(user, fest=False):
    usergroup = user.groups.values_list('name', flat=True).first()

    if fest:
        sperrzeiten = FesteSperrzeit.objects.order_by('-beginn')
    else:
        sperrzeiten = Sperrzeit.objects.order_by('-beginn')
    if usergroup == "Assistenten":
        sperrzeiten = sperrzeiten.filter(assistent=user.assistent)
    elif usergroup == "Assistenznehmer":
        sperrzeiten = sperrzeiten.filter(asn=user.assistenznehmer)
    if not fest:
        sperrzeiten = sperrzeiten.filter(beginn__gte=timezone.now())

    if fest:
        for sperrzeit in sperrzeiten:
            sperrzeit.wochentag = WTAGE[str(sperrzeit.wochentag)]
    return sperrzeiten


def sort_schichten_in_templates(asn, date):

    splitted_templates = []
    templates = get_schicht_templates(asn=asn, order_by='beginn')
    # Todo Sub-Templates und verschobene Templates
    for template in templates:
        if template.beginn < template.ende:

            splitted_templates.append(
                {
                    'beginn': template.beginn,
                    'ende': template.ende
                }
            )
        else:
            splitted_templates.append(
                {
                    'beginn': template.beginn,
                    'ende': time(0)
                }
            )
            splitted_templates.append(
                {
                    'beginn': time(0),
                    'ende': template.ende
                }
            )
    splitted_templates = sorted(splitted_templates, key=lambda j: j['beginn'])
    start = date

    # schichtsammlung durch ergänzung von leeren Tagen zu Kalender konvertieren
    end = shift_month(date, step=1)
    monatsletzter = (end - timedelta(days=1)).day

    schichten = get_sliced_schichten_by_asn(
        start=date,
        end=end,
        asn=asn
    )

    table_array = {}
    for i in range(1, monatsletzter + 1):
        datakey = datetime(year=date.year, month=date.month, day=i)
        template_counter = 0
        table_array[datakey] = {}
        for template in splitted_templates:
            temp_beginn = timezone.make_aware(datetime.combine(datakey, template['beginn']))
            if template['ende'] == time(0):
                temp_ende = timezone.make_aware(
                    datetime.combine(
                        datakey + timedelta(days=1),
                        template['ende']
                    )
                )
            else:
                temp_ende = timezone.make_aware(datetime.combine(datakey, template['ende']))
            table_array[datakey][template_counter] = []
            schicht_counter = 0
            for schicht in schichten:
                if schicht['beginn'] == temp_beginn and schicht['ende'] == temp_ende:
                    # Wenn sich mehrere Assistenten um die gleiche Schicht "bewerben",
                    # können mehrere Schichten im selben Template stehen

                    table_array[datakey][template_counter].append(schicht)
                    schichten.remove(schicht)
                    schicht_counter += 1

            if schicht_counter == 0:
                table_array[datakey][template_counter] = []
            template_counter += 1
    return splitted_templates, table_array
