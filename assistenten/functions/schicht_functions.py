from datetime import timedelta

from django.utils import timezone
from django.utils.datetime_safe import datetime

from assistenten.models import SchichtTemplate, FesteSchicht, Schicht, Adresse
from assistenten.views.assistenten.as_schicht_tabelle_view import check_mehrtaegig, get_ersten_xxtag, check_au, \
    check_urlaub


def get_schicht_templates(asn):
    # alle schicht_templates des asn
    schicht_template_liste = []
    schicht_templates = SchichtTemplate.objects.filter(
        asn=asn.id)
    for schicht_template in schicht_templates:
        schicht_template_liste.append({
            'id': schicht_template.id,
            'bezeichner': schicht_template.bezeichner,
            'beginn': schicht_template.beginn.strftime("%H:%M"),
            'ende': schicht_template.ende.strftime("%H:%M"),
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

    wtage = {'0': 'Mo', '1': 'Di', '2': 'Mi', '3': 'Do', '4': 'Fr', '5': 'Sa', '6': 'So'}

    for feste_schicht in feste_schichten:
        feste_schichten_liste.append({
            'id': feste_schicht.id,
            'wochentag': wtage[feste_schicht.wochentag],
            'beginn': feste_schicht.beginn.strftime("%H:%M"),
            'ende': feste_schicht.ende.strftime("%H:%M"),
        })
    return feste_schichten_liste


def get_sliced_schichten(start, end, asn):
    schichten = \
        Schicht.objects.filter(beginn__range=(start, end)).filter(asn=asn) | \
        Schicht.objects.filter(ende__range=(start, end)).filter(asn=asn)

    sliced_schichten = []
    for schicht in schichten:
        ergebnisse = split_by_null_uhr(schicht)
        for ergebnis in ergebnisse:
            sliced_schichten.append(ergebnis)

    return sliced_schichten


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


def add_feste_schichten(erster_tag, letzter_tag, asn):
    feste_schichten = FesteSchicht.objects.filter(asn=asn)

    for feste_schicht in feste_schichten:
        wtag_int = int(feste_schicht.wochentag)
        erster_xxtag_des_monats = get_ersten_xxtag(wtag_int, erster_tag)
        monat = erster_tag.month
        year = erster_tag.year
        maxday = (letzter_tag - timedelta(days=1)).day
        assi = feste_schicht.assistent
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
                if not check_au(datum=start, assistent=assi) and \
                        not check_urlaub(datum=start, assistent=assi) and \
                        not check_au(datum=end - timedelta(minutes=1), assistent=assi) \
                        and not check_urlaub(datum=end - timedelta(minutes=1), assistent=assi):
                    home = Adresse.objects.filter(is_home=True).filter(asn=asn)[0]
                    schicht_neu = Schicht(beginn=start,
                                          ende=end,
                                          asn=asn,
                                          assistent=assi,
                                          beginn_adresse=home,
                                          ende_adresse=home)
                    schicht_neu.save()
