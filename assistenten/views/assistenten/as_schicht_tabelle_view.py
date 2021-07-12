from datetime import timedelta
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.utils.datetime_safe import datetime
from django.views.generic import TemplateView
from assistenten.models import Schicht, Lohn, Urlaub, Brutto, AU, FesteSchicht, Adresse


def berechne_ostern(jahr):
    # Berechnung von Ostern mittels Gaußscher Osterformel
    # siehe http://www.ptb.de/de/org/4/44/441/oste.htm
    # mindestens bis 2031 richtig
    K = jahr // 100
    M = 15 + ((3 * K + 3) // 4) - ((8 * K + 13) // 25)
    S = 2 - ((3 * K + 3) // 4)
    A = jahr % 19
    D = (19 * A + M) % 30
    R = (D + (A // 11)) // 29
    OG = 21 + D - R
    SZ = 7 - (jahr + (jahr // 4) + S) % 7
    OE = 7 - ((OG - SZ) % 7)

    tmp = OG + OE  # das Osterdatum als Tages des März, also 32 entspricht 1. April
    m = 0
    if tmp > 31:  # Monat erhöhen, tmp=tag erniedriegen
        m = tmp // 31
        if tmp == 31:
            m = 0
        tmp = tmp - 31

    return timezone.make_aware(datetime(year=jahr, month=3 + m, day=tmp))


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


def check_feiertag(datum):
    jahr = datum.year
    feiertage = []
    feiertag = {'name': 'Neujahr', 'd': 1, 'm': 1, 'Y': 0}
    feiertage.append(feiertag)
    feiertag = {'name': 'Internationaler Frauentag', 'd': 8, 'm': 3, 'Y': 0}
    feiertage.append(feiertag)
    feiertag = {'name': 'Tag der Arbeit', 'd': 1, 'm': 5, 'Y': 0}
    feiertage.append(feiertag)
    feiertag = {'name': 'Tag der deutschen Einheit', 'd': 3, 'm': 10, 'Y': 0}
    feiertage.append(feiertag)
    feiertag = {'name': '1. Weihnachtsfeiertagt', 'd': 25, 'm': 12, 'Y': 0}
    feiertage.append(feiertag)
    feiertag = {'name': '2. Weihnachtsfeiertag', 'd': 26, 'm': 12, 'Y': 0}
    feiertage.append(feiertag)
    feiertag = {'name': 'Tag der Befreiung', 'd': 26, 'm': 12, 'Y': 2020}
    feiertage.append(feiertag)

    # kein Feiertag in Berlin TODO Prio = 1000, andere Bundesländer
    ostersonntag = berechne_ostern(jahr)
    karfreitag = ostersonntag - timedelta(days=2)
    feiertag = {'name': 'Karfreitag', 'd': int(karfreitag.strftime('%d')),
                'm': int(karfreitag.strftime('%m')), 'Y': 0}
    feiertage.append(feiertag)
    ostermontag = ostersonntag + timedelta(days=1)
    feiertag = {'name': 'Ostermontag', 'd': int(ostermontag.strftime('%d')),
                'm': int(ostermontag.strftime('%m')), 'Y': 0}
    feiertage.append(feiertag)
    himmelfahrt = ostersonntag + timedelta(days=40)
    feiertag = {'name': 'Christi Himmelfahrt', 'd': int(himmelfahrt.strftime('%d')),
                'm': int(himmelfahrt.strftime('%m')), 'Y': 0}
    feiertage.append(feiertag)
    pfingstsonntag = ostersonntag + timedelta(days=49)
    feiertag = {'name': 'Pfingstsonntag', 'd': int(pfingstsonntag.strftime('%d')),
                'm': int(pfingstsonntag.strftime('%m')), 'Y': 0}
    feiertage.append(feiertag)
    pfingstmontag = ostersonntag + timedelta(days=50)
    feiertag = {'name': 'Pfingstmontag', 'd': int(pfingstmontag.strftime('%d')),
                'm': int(pfingstmontag.strftime('%m')), 'Y': 0}
    feiertage.append(feiertag)
    ausgabe = ''
    for feiertag in feiertage:
        if feiertag['Y'] > 0:
            if feiertag['Y'] == datum.year \
                    and datum.day == feiertag['d'] \
                    and datum.month == feiertag['m']:
                ausgabe = feiertag['name']
                break
        elif feiertag['Y'] == 0:
            if datum.day == feiertag['d'] and datum.month == feiertag['m']:
                ausgabe = feiertag['name']
                break
    return ausgabe


def check_schicht(datum: datetime):
    """prüft, ob an einem gegeben Datum eine Schicht ist."""
    tagbeginn = timezone.make_aware(datetime(year=datum.year,
                                             month=datum.month,
                                             day=datum.day,
                                             hour=0,
                                             minute=0,
                                             second=0))
    tagende = timezone.make_aware(datetime(year=datum.year,
                                           month=datum.month,
                                           day=datum.day,
                                           hour=23,
                                           minute=59,
                                           second=59))

    # alle schichten, die "heute" anfangen, heute enden oder vor heute anfangen und nach heute enden.
    schichten = Schicht.objects.filter(beginn__range=(tagbeginn, tagende)) | Schicht.objects.filter(
        ende__range=(tagbeginn, tagende)) | Schicht.objects.filter(beginn__lte=tagbeginn).filter(ende__gte=tagende)
    if schichten:
        return True
    return False


def get_monatserster(datum):
    return timezone.make_aware(datetime(year=datum.year,
                                        month=datum.month,
                                        day=1))


def get_ersten_xxtag(int_weekday, erster=datetime.now()):
    for counter in range(1, 8):
        if timezone.make_aware(datetime(year=erster.year, month=erster.month, day=counter, hour=0,
                                        minute=0)).weekday() == int_weekday:
            return counter


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


def get_sliced_schichten(start, end, assistent):
    schichten = \
        Schicht.objects.filter(beginn__range=(start, end)).filter(assistent=assistent) | \
        Schicht.objects.filter(ende__range=(start, end)).filter(assistent=assistent)

    sliced_schichten = []
    for schicht in schichten:
        ergebnisse = split_by_null_uhr(schicht)
        for ergebnis in ergebnisse:
            sliced_schichten.append(ergebnis)

    return sliced_schichten


def get_duration(then, now=timezone.now(), interval="default"):
    # Returns a duration as specified by variable interval
    # Functions, except totalDuration, returns [quotient, remainder]

    duration = now - then  # For build-in functions
    duration_in_s = duration.total_seconds()

    def years():
        return divmod(duration_in_s, 31536000)  # Seconds in a year=31536000.

    def days(secs=None):
        return divmod(secs if secs is not None else duration_in_s, 86400)  # Seconds in a day = 86400

    def hours(secs=None):
        return divmod(secs if secs is not None else duration_in_s, 3600)  # Seconds in an hour = 3600

    def minutes(secs=None):
        return divmod(secs if secs is not None else duration_in_s, 60)  # Seconds in a minute = 60

    def seconds(secs=None):
        if secs is not None:
            return divmod(secs, 1)
        return duration_in_s

    def total_duration():
        y = years()
        d = days(y[1])  # Use remainder to calculate next variable
        h = hours(d[1])
        m = minutes(h[1])
        s = seconds(m[1])

        return "Time between dates: {} years, {} days, {} hours, {} minutes and {} seconds".format(int(y[0]),
                                                                                                   int(d[0]),
                                                                                                   int(h[0]),
                                                                                                   int(m[0]),
                                                                                                   int(s[0]))

    return {
        'years': int(years()[0]),
        'days': int(days()[0]),
        'hours': int(hours()[0]),
        'minutes': int(minutes()[0]),
        'seconds': int(seconds()),
        'default': total_duration()
    }[interval]


def get_first_of_next_month(this_month: datetime):
    year = this_month.year
    month = this_month.month + 1
    day = 1
    if month == 13:
        month = 1
        year += 1
    return timezone.make_aware(datetime(year=year, month=month, day=day))


def sort_schicht_data_by_beginn(schichten: list):
    """sortiert die schichten an einem tag (in Form einer Liste von dicts von strings)
    nach ihrem beginn"""
    ausgabe = []

    for schicht in schichten:
        insert_flag = False
        beginn_akt_schicht = schicht['von']
        for zaehler in range(0, len(ausgabe)):
            if beginn_akt_schicht < ausgabe[zaehler]['von']:
                ausgabe.insert(zaehler, schicht)
                insert_flag = True
                break
        if not insert_flag:
            ausgabe.append(schicht)

    return ausgabe


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


def shift_month(date: datetime, step: int = 1):
    act_date = date
    if step > 0:
        for i in range(0, step):
            nachmonat = {
                'year': act_date.year,
                'month': act_date.month + 1,

            }
            if nachmonat['month'] == 13:
                nachmonat['month'] = 1
                nachmonat['year'] += 1

            act_date = timezone.make_aware(datetime(year=nachmonat['year'], month=nachmonat['month'], day=1))
    elif step < 0:
        for i in range(0, abs(step)):
            nachmonat = {
                'year': act_date.year,
                'month': act_date.month - 1,

            }
            if nachmonat['month'] == 0:
                nachmonat['month'] = 12
                nachmonat['year'] -= 1

            act_date = timezone.make_aware(datetime(year=nachmonat['year'], month=nachmonat['month'], day=1))

    return act_date


def add_feste_schichten(erster_tag, letzter_tag, assistent):
    feste_schichten = FesteSchicht.objects.filter(assistent=assistent)

    for feste_schicht in feste_schichten:
        wtag_int = int(feste_schicht.wochentag)
        erster_xxtag_des_monats = get_ersten_xxtag(wtag_int, erster_tag)
        monat = erster_tag.month
        year = erster_tag.year
        maxday = (letzter_tag - timedelta(days=1)).day
        asn = feste_schicht.asn
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
                if not check_au(datum=start, assistent=assistent) and \
                        not check_urlaub(datum=start, assistent=assistent) and \
                        not check_au(datum=end - timedelta(minutes=1), assistent=assistent) \
                        and not check_urlaub(datum=end - timedelta(minutes=1), assistent=assistent):
                    home = Adresse.objects.filter(is_home=True).filter(asn=asn)[0]
                    schicht_neu = Schicht(beginn=start,
                                          ende=end,
                                          asn=asn,
                                          assistent=assistent,
                                          beginn_adresse=home,
                                          ende_adresse=home)
                    schicht_neu.save()


class AsSchichtTabellenView(LoginRequiredMixin, TemplateView):
    model = Schicht
    context_object_name = 'as_schicht_tabellen_monat'
    template_name = 'assistenten/show_AsSchichtTabelle.html'
    act_date = timezone.now()
    schichten_view_data = {}
    summen = {
        'arbeitsstunden': 0,
        'stundenlohn': 0,
        'lohn': 0,
        'nachtstunden': 0,
        'nachtzuschlag': 0,
        'nachtzuschlag_kumuliert': 0,
        'bsd': 0,
        'bsd_stunden': 0,
        'bsd_kumuliert': 0,
        'wegegeld_bsd': 0,
        'orga_zuschlag': 0,
        'orga_zuschlag_kumuliert': 0,
        'wechselschicht_zuschlag': 0,
        'wechselschicht_zuschlag_kumuliert': 0,
        'freizeitausgleich': 0,
        'bruttolohn': 0,
        'anzahl_feiertage': 0,
        'freie_sonntage': 52,
        'moegliche_arbeitssonntage': 37,
        'urlaubsstunden': 0,
        'stundenlohn_urlaub': 0,
        'urlaubslohn': 0,
        'austunden': 0,
        'stundenlohn_au': 0,
        'aulohn': 0,
        'ueberstunden': 0,
        'ueberstunden_pro_stunde': 0,
        'ueberstunden_kumuliert': 0,
        'zuschlaege': {}

    }

    def get_context_data(self, **kwargs):
        self.reset()
        # Call the base implementation first to get a context
        if 'year' in self.request.GET:
            self.act_date = timezone.make_aware(datetime(year=int(self.request.GET['year']),
                                                         month=int(self.request.GET['month']),
                                                         day=1))
        elif 'year' in kwargs:
            self.act_date = timezone.make_aware(datetime(year=int(kwargs['year']),
                                                         month=int(kwargs['month']),
                                                         day=1))
        else:
            self.act_date = get_monatserster(timezone.now())

        context = super().get_context_data(**kwargs)
        context['nav_timedelta'] = self.get_time_navigation_data()
        context['schichttabelle'] = self.get_table_data()
        self.calc_add_sum_data()
        context['summen'] = self.summen

        # brutto in db speichern
        brutto_in_db(
            brutto=self.summen['bruttolohn'],
            stunden=self.summen['arbeitsstunden'],
            monat=self.act_date,
            assistent=self.request.user.assistent
        )

        self.reset()
        return context

    def calc_add_sum_data(self):
        # print(self.summen)
        self.calc_freizeitausgleich()
        # print(self.summen)
        self.calc_ueberstunden_zuschlag()
        # print(self.summen)
        self.summen['freie_sonntage'] = self.calc_freie_sonntage()
        self.summen['moegliche_arbeitssonntage'] = self.summen['freie_sonntage'] - 15
        # print(self.summen)

        self.summen['bruttolohn'] = float(
            self.summen['lohn']) + float(
            self.summen['nachtzuschlag_kumuliert']) + float(
            self.summen['orga_zuschlag_kumuliert']) + float(
            self.summen['wechselschicht_zuschlag_kumuliert']) + float(
            self.summen['bsd_kumuliert']) + float(
            self.summen['urlaubslohn']) + float(
            self.summen['aulohn']) + float(
            self.summen['freizeitausgleich']) + float(
            self.summen['ueberstunden_kumuliert'])

        for zuschlag in self.summen['zuschlaege'].values():
            self.summen['bruttolohn'] += float(zuschlag['kumuliert'])

    def calc_freizeitausgleich(self):
        # anzahl aller feiertage ermitteln
        start = get_monatserster(self.act_date)
        end = get_first_of_next_month(start)

        letzter_tag = (end - timedelta(seconds=1)).day
        ausgleichsstunden = berechne_urlaub_au_saetze(datum=start,
                                                      assistent=self.request.user.assistent)['stunden_pro_tag']
        ausgleichslohn = berechne_urlaub_au_saetze(datum=start,
                                                   assistent=self.request.user.assistent)['pro_stunde']
        for tag in range(1, letzter_tag + 1):
            if check_feiertag(datetime(year=start.year, month=start.month, day=tag)):
                self.summen['anzahl_feiertage'] += 1
                self.summen['freizeitausgleich'] += ausgleichslohn * ausgleichsstunden

    def calc_ueberstunden_zuschlag(self):
        # überstunden
        ueberstunden = self.summen['arbeitsstunden'] + self.summen['urlaubsstunden'] + self.summen['austunden'] - 168.5
        if ueberstunden > 0:
            lohn = get_lohn(assistent=self.request.user.assistent, datum=self.act_date)
            self.summen['ueberstunden'] = ueberstunden
            self.summen['ueberstunden_pro_stunde'] = float(lohn.ueberstunden_zuschlag)
            self.summen['ueberstunden_kumuliert'] = float(lohn.ueberstunden_zuschlag) * ueberstunden

    def calc_freie_sonntage(self):
        year = self.act_date.year
        # erster sonntag
        janfirst = datetime(year, 1, 1)
        sunday = (7 - janfirst.weekday()) % 7
        sunday = 7 if sunday == 0 else sunday
        sunday = timezone.make_aware(datetime(year=year,
                                              month=1,
                                              day=sunday))

        wochencounter = 0
        sontagsschichtcounter = 0
        for kw in range(1, 54):
            if sunday.year == year:
                wochencounter += 1
                # print('---------------')
                if check_schicht(sunday):
                    sontagsschichtcounter += 1

            sunday = sunday + timedelta(days=7)

        return wochencounter - sontagsschichtcounter

    def calc_schichten(self, start, ende):

        schichten = get_sliced_schichten(
            start=self.act_date,
            end=ende,
            assistent=self.request.user.assistent
        )

        # feste Schichten
        if not schichten:
            add_feste_schichten(erster_tag=start, letzter_tag=ende, assistent=self.request.user.assistent)
            schichten = get_sliced_schichten(
                start=self.act_date,
                end=ende,
                assistent=self.request.user.assistent
            )

        for schicht in schichten:
            if not schicht['beginn'].strftime('%d') in self.schichten_view_data.keys():
                self.schichten_view_data[schicht['beginn'].strftime('%d')] = []

            # at etc
            asn_add = ''
            asn_add += 'AT ' if schicht['ist_assistententreffen'] else ''
            asn_add += 'PCG ' if schicht['ist_pcg'] else ''
            asn_add += 'RB/BSD ' if schicht['ist_kurzfristig'] else ''
            asn_add += 'AFG ' if schicht['ist_ausfallgeld'] else ''

            # stunden
            stunden = berechne_stunden(schicht)

            lohn = get_lohn(assistent=self.request.user.assistent, datum=schicht['beginn'])

            nachtstunden = get_nachtstunden(schicht)

            # zuschläge
            zuschlaege = berechne_sa_so_weisil_feiertagszuschlaege(schicht)
            zuschlaege_text = ''

            if zuschlaege:
                if zuschlaege['stunden_gesamt'] > 0:
                    grund = zuschlaege['zuschlagsgrund']
                    # Grund zu lower-case mit "_" statt " " und ohne punkte,
                    # damit es dem Spaltennamen der Tabelle entspricht
                    grund_formatiert = grund.lower().replace('.', '').replace(' ', '_')
                    spaltenname = grund_formatiert + '_zuschlag'
                    stundenzuschlag = float(getattr(lohn, spaltenname))
                    schichtzuschlag = zuschlaege['stunden_gesamt'] * stundenzuschlag
                    zuschlaege_text = grund + ': ' + "{:,.2f}".format(
                        zuschlaege['stunden_gesamt']
                    ) + ' Std = ' + "{:,.2f}€".format(schichtzuschlag)

                    # in Summen
                    # print(self.summen['zuschlaege'])
                    if grund_formatiert in self.summen['zuschlaege']:
                        self.summen['zuschlaege'][grund_formatiert]["stunden"] += zuschlaege['stunden_gesamt']
                        self.summen['zuschlaege'][grund_formatiert]["kumuliert"] += schichtzuschlag
                    else:
                        self.summen['zuschlaege'][grund_formatiert] = \
                            {
                                'bezeichner': grund,
                                'stunden': zuschlaege['stunden_gesamt'],
                                'pro_stunde': stundenzuschlag,
                                'kumuliert': schichtzuschlag
                            }

            schicht_id = schicht['schicht_id']

            asn_add += schicht['asn'].kuerzel if schicht['asn'] else ''
            self.schichten_view_data[schicht['beginn'].strftime('%d')].append(
                {
                    'schicht_id': schicht_id,
                    'von': schicht['beginn'],
                    'bis': schicht['ende'],
                    'asn': asn_add,
                    'stunden': stunden,
                    'stundenlohn': lohn.grundlohn,
                    'schichtlohn': float(lohn.grundlohn) * stunden,
                    'bsd': float(lohn.grundlohn) * stunden * (
                            lohn.kurzfristig_zuschlag_prozent / 100) if schicht['ist_kurzfristig'] else 0,
                    'orgazulage': lohn.orga_zuschlag,
                    'orgazulage_schicht': float(lohn.orga_zuschlag) * stunden,
                    'wechselzulage': lohn.wechselschicht_zuschlag,
                    'wechselzulage_schicht': float(lohn.wechselschicht_zuschlag) * stunden,
                    'nachtstunden': nachtstunden,
                    'nachtzuschlag': lohn.nacht_zuschlag,
                    'nachtzuschlag_schicht': float(lohn.nacht_zuschlag) * nachtstunden,
                    'zuschlaege': zuschlaege_text,
                    'type': 'schicht'
                }
            )

            # daten für Summen-Tabelle

            self.summen['arbeitsstunden'] += stunden
            self.summen['stundenlohn'] = lohn.grundlohn
            self.summen['lohn'] += stunden * float(lohn.grundlohn)
            self.summen['nachtstunden'] += nachtstunden
            self.summen['nachtzuschlag'] = lohn.nacht_zuschlag
            self.summen['nachtzuschlag_kumuliert'] += nachtstunden * float(lohn.nacht_zuschlag)
            self.summen['bsd_stunden'] += stunden if 'ist_kurzfristig' in schicht and schicht['ist_kurzfristig'] else 0
            self.summen['bsd_lohn'] = (lohn.kurzfristig_zuschlag_prozent / 100) * lohn.grundlohn \
                if 'ist_kurzfristig' in schicht and schicht['ist_kurzfristig'] else 0
            self.summen['bsd_kumuliert'] += (float(
                lohn.kurzfristig_zuschlag_prozent / 100 * lohn.grundlohn) * stunden) \
                if 'ist_kurzfristig' in schicht and schicht['ist_kurzfristig'] else 0
            # self.summen['bsd_wegegeld'] += 0  # TODO
            self.summen['orga_zuschlag'] = lohn.orga_zuschlag
            self.summen['orga_zuschlag_kumuliert'] += float(lohn.orga_zuschlag) * stunden
            self.summen['wechselschicht_zuschlag'] = lohn.wechselschicht_zuschlag
            self.summen['wechselschicht_zuschlag_kumuliert'] += float(lohn.wechselschicht_zuschlag) * stunden

        # Deckelung des Wechselschichtzuschlages:
        if self.summen['wechselschicht_zuschlag_kumuliert'] > 105:
            self.summen['wechselschicht_zuschlag_kumuliert'] = 105
            # mehrere Schichten an jedem Tag nach schichtbeginn sortieren
        for key in self.schichten_view_data:
            self.schichten_view_data[key] = sort_schicht_data_by_beginn(self.schichten_view_data[key])

    def calc_urlaube(self, start, ende):
        # Urlaube ermitteln
        # es soll kein urlaub gefunden werden, der genau am nächsten monatsersten um 0:00 Uhr beginnt
        ende = ende - timedelta(minutes=2)
        # finde alle urlaube, der anfang, ende oder mitte (anfang ist vor beginn und ende nach ende dieses Monats)
        # in diesem Urlaub liegt
        urlaube = \
            Urlaub.objects.filter(beginn__range=(start, ende)).filter(assistent=self.request.user.assistent) | \
            Urlaub.objects.filter(ende__range=(start, ende)).filter(assistent=self.request.user.assistent) | \
            Urlaub.objects.filter(beginn__lte=start).filter(
                ende__gte=ende).filter(assistent=self.request.user.assistent)

        for urlaub in urlaube:
            erster_tag = urlaub.beginn.day if urlaub.beginn > start.date() else start.day
            letzter_tag = urlaub.ende.day if urlaub.ende < ende.date() else (ende - timedelta(days=1)).day
            urlaubsstunden = berechne_urlaub_au_saetze(datum=start,
                                                       assistent=self.request.user.assistent)['stunden_pro_tag']
            urlaubslohn = berechne_urlaub_au_saetze(datum=start,
                                                    assistent=self.request.user.assistent)['pro_stunde']
            for tag in range(erster_tag, letzter_tag + 2):
                # print(tag)
                if tag not in self.schichten_view_data.keys():
                    self.schichten_view_data["{:02d}".format(tag)] = []
                self.schichten_view_data["{:02d}".format(tag)].append(
                    {
                        'schicht_id': urlaub.id,
                        'von': '',
                        'bis': '',
                        'asn': 'Urlaub',
                        'stunden': urlaubsstunden,
                        'stundenlohn': urlaubslohn,
                        'schichtlohn': urlaubslohn * urlaubsstunden,
                        'bsd': 0,
                        'orgazulage': 0,
                        'orgazulage_schicht': 0,
                        'wechselzulage': 0,
                        'wechselzulage_schicht': 0,
                        'nachtstunden': 0,
                        'nachtzuschlag': 0,
                        'nachtzuschlag_schicht': 0,
                        'zuschlaege': 0,
                        'type': 'urlaub'
                    }
                )

                self.summen['urlaubsstunden'] += urlaubsstunden
                self.summen['stundenlohn_urlaub'] = urlaubslohn
                self.summen['urlaubslohn'] += urlaubsstunden * urlaubslohn

    def calc_au(self, start, ende):
        # AU ermitteln

        # es soll keine au gefunden werden, die genau am nächsten monatsersten um 0:00 Uhr beginnt
        ende = ende - timedelta(minutes=2)
        # finde alle AU, der anfang, ende oder mitte (anfang ist vor beginn und ende nach ende dieses Monats)
        # in diesem AU liegt
        aus = \
            AU.objects.filter(beginn__range=(start, ende)).filter(assistent=self.request.user.assistent) | \
            AU.objects.filter(ende__range=(start, ende)).filter(assistent=self.request.user.assistent) | \
            AU.objects.filter(beginn__lte=start).filter(ende__gte=ende).filter(assistent=self.request.user.assistent)

        for au in aus:
            erster_tag = au.beginn.day if au.beginn > start.date() else start.day
            letzter_tag = au.ende.day if au.ende < ende.date() else (ende - timedelta(days=1)).day
            austunden = berechne_urlaub_au_saetze(datum=start,
                                                  assistent=self.request.user.assistent)['stunden_pro_tag']
            aulohn = berechne_urlaub_au_saetze(datum=start,
                                               assistent=self.request.user.assistent)['pro_stunde']

            for tag in range(erster_tag, letzter_tag + 1):
                # print(tag)
                if tag not in self.schichten_view_data.keys():
                    self.schichten_view_data["{:02d}".format(tag)] = []
                self.schichten_view_data["{:02d}".format(tag)].append(
                    {
                        'schicht_id': au.id,
                        'von': '',
                        'bis': '',
                        'asn': 'AU/krank',
                        'stunden': austunden,
                        'stundenlohn': aulohn,
                        'schichtlohn': aulohn * austunden,
                        'bsd': 0,
                        'orgazulage': 0,
                        'orgazulage_schicht': 0,
                        'wechselzulage': 0,
                        'wechselzulage_schicht': 0,
                        'nachtstunden': 0,
                        'nachtzuschlag': 0,
                        'nachtzuschlag_schicht': 0,
                        'zuschlaege': 0,
                        'type': 'au'
                    }
                )
                self.summen['austunden'] += austunden
                self.summen['stundenlohn_au'] = aulohn
                self.summen['aulohn'] += austunden * aulohn

    def get_table_data(self):
        # TODO optimieren!!!

        start = self.act_date
        ende = get_first_of_next_month(this_month=start)

        # schichten berechnen und in schicht_view_data bzw. summen einsortieren
        self.calc_schichten(start=start, ende=ende)

        # urlaube berechnen und in schicht_view_data bzw. summen einsortieren
        self.calc_urlaube(start=start, ende=ende)

        # au/krank berechnen und in schicht_view_data bzw. summen einsortieren
        self.calc_au(start=start, ende=ende)

        # schichtsammlung durch ergänzung von leeren Tagen zu Kalender konvertieren
        monatsletzter = (shift_month(self.act_date, step=1) - timedelta(days=1)).day
        table_array = {}
        for i in range(1, monatsletzter + 1):
            key = str(i).zfill(2)
            datakey = datetime(year=self.act_date.year, month=self.act_date.month, day=i)
            if key in self.schichten_view_data:
                table_array[datakey] = self.schichten_view_data[key]
            else:
                table_array[datakey] = []

        return table_array

    def get_time_navigation_data(self):
        # test
        if 'act_date' in self.request.POST:
            self.act_date = self.request.POST['act_date']

        if 'year' in self.request.POST:
            self.act_date = timezone.make_aware(datetime(year=self.request.POST['year'],
                                                         month=self.request.POST['month'],
                                                         day=1))

        act_date = get_monatserster(self.act_date)
        vormonat_date = shift_month(get_monatserster(self.act_date), step=-1)
        nachmonat_date = shift_month(get_monatserster(self.act_date), step=1)
        monatsliste = {}
        for i in range(1, 13):
            monatsliste[
                datetime(month=i,
                         year=1,
                         day=1).strftime('%m')] = datetime(month=i,
                                                           year=1,
                                                           day=1).strftime('%b')
        jahresliste = []
        for j in range(datetime.now().year + 2, datetime.now().year - 40, -1):
            jahresliste.append(str(j))

        return {
            'act_date': act_date,
            'vormonat_date': vormonat_date,
            'nachmonat_date': nachmonat_date,
            'monatsliste': monatsliste,
            'jahresliste': jahresliste
        }

    def reset(self):
        self.schichten_view_data = {}
        self.summen = {
            'arbeitsstunden': 0,
            'stundenlohn': 0,
            'lohn': 0,
            'nachtstunden': 0,
            'nachtzuschlag': 0,
            'nachtzuschlag_kumuliert': 0,
            'bsd': 0,
            'bsd_stunden': 0,
            'bsd_kumuliert': 0,
            'wegegeld_bsd': 0,
            'orga_zuschlag': 0,
            'orga_zuschlag_kumuliert': 0,
            'wechselschicht_zuschlag': 0,
            'wechselschicht_zuschlag_kumuliert': 0,
            'freizeitausgleich': 0,
            'bruttolohn': 0,
            'anzahl_feiertage': 0,
            'freie_sonntage': 52,
            'moegliche_arbeitssonntage': 37,
            'urlaubsstunden': 0,
            'stundenlohn_urlaub': 0,
            'urlaubslohn': 0,
            'austunden': 0,
            'stundenlohn_au': 0,
            'aulohn': 0,
            'ueberstunden': 0,
            'ueberstunden_pro_stunde': 0,
            'ueberstunden_kumuliert': 0,
            'zuschlaege': {}

        }
