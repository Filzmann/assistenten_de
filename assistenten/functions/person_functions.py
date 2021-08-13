from assistenten.models import Adresse, Assistent, ASN


def get_address(assistent=False, asn=False, is_home=False):
    adressen = Adresse.objects

    if assistent:
        if isinstance(assistent, int):
            asn=Assistent.objects.get(id=assistent)
        adressen=adressen.filter(assistent=assistent)
    if asn:
        if isinstance(asn, int):
            asn=ASN.objects.get(id=asn)
        adressen=adressen.filter(asn=asn)
    if is_home:
        adressen=adressen.filter(is_home=True)
    return adressen
