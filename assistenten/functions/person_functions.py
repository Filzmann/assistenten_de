from assistenten.models import Adresse


def get_address(assistent=False, asn=False, is_home=False):
    adressen = Adresse.objects
    if assistent:
        adressen=adressen.filter(assistent=assistent)
    if asn:
        adressen=adressen.filter(asn=asn)
    if is_home:
        adressen=adressen.filter(is_home=True)
        
    return adressen
