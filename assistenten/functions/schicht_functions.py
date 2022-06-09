from datetime import timedelta
from django.db.models import Q
from assistenten.models import Schicht, Brutto, AU, Urlaub


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
