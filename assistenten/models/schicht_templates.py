from django.db import models

from assistenten.models.assistenznehmer import ASN


class SchichtTemplate(models.Model):
    # relationships
    asn = models.ForeignKey(ASN, on_delete=models.CASCADE)

    # extra data
    beginn = models.DateTimeField()
    ende = models.DateTimeField()
    bezeichner = models.CharField(max_length=30)

    def __repr__(self):
        return f"Template({self.bezeichner!r}, {self.beginn!r} - {self.ende!r})"
