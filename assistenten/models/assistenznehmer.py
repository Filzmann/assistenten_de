from django.db import models

from assistenten.models import EB, PFK


class ASN(models.Model):

    kuerzel = models.CharField(max_length=30)
    name = models.CharField(max_length=30)
    vorname = models.CharField(max_length=30)
    email = models.CharField(max_length=30)
    einsatzbuero = models.CharField(max_length=30)

    einsatzbegleitung = models.ForeignKey(EB, on_delete=models.CASCADE, related_name='asn')
    pflegefachkraft = models.ForeignKey(PFK, on_delete=models.CASCADE, related_name='asn')

    def __repr__(self):
        return f"ASN(Kürzel={self.kuerzel!r}, Name={self.name!r}, Vorname={self.vorname!r})"