from datetime import timedelta

from django.utils import timezone
from django.utils.datetime_safe import datetime

from assistenten.functions.schicht_functions import check_schicht


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


def get_monatserster(datum):
    return timezone.make_aware(datetime(year=datum.year,
                                        month=datum.month,
                                        day=1))


def get_ersten_xxtag(int_weekday, erster=datetime.now()):
    for counter in range(1, 8):
        if timezone.make_aware(datetime(year=erster.year, month=erster.month, day=counter, hour=0,
                                        minute=0)).weekday() == int_weekday:
            return counter


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


def calc_freie_sonntage(act_date, assistent):
    year = act_date.year
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
            if check_schicht(
                    beginn=sunday,
                    ende=sunday + timedelta(hours=23, minutes=59, seconds=59),
                    assistent=assistent
            ):
                sontagsschichtcounter += 1

        sunday = sunday + timedelta(days=7)

    return wochencounter - sontagsschichtcounter