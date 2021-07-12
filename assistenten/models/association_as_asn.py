from django.db import models
from assistenten.models import Assistent, ASN


class AssociationAsAsn(models.Model):
    assistent = models.ForeignKey(Assistent, on_delete=models.CASCADE)
    asn = models.ForeignKey(ASN, on_delete=models.CASCADE)
    is_festes_team = models.BooleanField(default=0)
    is_vertretungsteam = models.BooleanField(default=0)

