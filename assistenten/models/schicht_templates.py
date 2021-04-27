from django.db import models

from assistenten.models.assistenznehmer import ASN


class SchichtTemplate(models.Model):
    # relationships
    asn = models.ForeignKey(ASN, on_delete=models.CASCADE)

    # extra data
    beginn = models.TimeField()
    ende = models.TimeField()
    bezeichner = models.CharField(max_length=30)

    def __repr__(self):
        return f"Template({self.bezeichner!r}, {self.beginn!r} - {self.ende!r})"

    def __str__(self):
        return f"{self.bezeichner}, {self.beginn.strftime('%H:%M')} - {self.ende.strftime('%H:%M')}"
