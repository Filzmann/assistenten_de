from assistenten.models import Adresse


def get_address(assistent=False, asn=False, is_home=False):
    adressen = Adresse.objects.filter(asn=asn)
    return adressen
