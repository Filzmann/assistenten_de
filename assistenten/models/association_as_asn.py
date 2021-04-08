from django.db import models
from assistenten.models import Assistent, ASN


class AssociationAsAsn(models.Model):
    assistent = models.ForeignKey(Assistent, on_delete=models.CASCADE)
    asn = models.ForeignKey(ASN, on_delete=models.CASCADE)
    fest_vertretung = models.CharField(max_length=50)


def get_assistents_by_asn(self, asn):
    assocs = AssociationAsAsn.objects.filter(asn=asn)


def get_asns_by_assistent(self, assistent):
    pass
