from django.contrib.auth.models import User
from django.db import models

from assistenten.models import EB, PFK
from assistenten.models.abstract_person import AbstractPerson


class ASN(AbstractPerson):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='assistenznehmer')
    kuerzel = models.CharField(max_length=30)
    einsatzbuero = models.CharField(max_length=30)

    einsatzbegleitung = models.ForeignKey(EB, on_delete=models.CASCADE, related_name='asns', null=True)
    pflegefachkraft = models.ForeignKey(PFK, on_delete=models.CASCADE, related_name='asns', null=True)


    def __repr__(self):
        return f"ASN(Kürzel={self.kuerzel!r}, Name={self.name!r}, Vorname={self.vorname!r})"

    def __str__(self):
        return f"{self.kuerzel} - {self.name}, {self.vorname}"
