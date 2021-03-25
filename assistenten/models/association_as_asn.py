from django.db import models
from assistenten.models import Assistent, ASN


class AssociationAsAsn(models.Model):
    assistent = models.ForeignKey(Assistent, on_delete=models.CASCADE)
    asn = models.ForeignKey(ASN, on_delete=models.CASCADE)
    fest_vertretung = models.CharField(max_length=50)
