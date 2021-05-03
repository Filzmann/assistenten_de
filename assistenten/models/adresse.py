from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from assistenten.models import Assistent, ASN


class Adresse(models.Model):
    bezeichner = models.CharField(max_length=30)
    strasse = models.CharField(max_length=30)
    hausnummer = models.CharField(max_length=8)
    plz = models.CharField(max_length=5)
    stadt = models.CharField(max_length=30)
    is_home = models.BooleanField(default=False)

    assistent = models.ForeignKey(Assistent, related_name='adressen', on_delete=models.CASCADE, null=True, blank=True)
    asn = models.ForeignKey(ASN, related_name='adressen', on_delete=models.CASCADE, null=True, blank=True)

    def __repr__(self):
        return f"Address(bezeichner={self.bezeichner!r}, " \
               f"strasse={self.strasse!r}, " \
               f"hausnummer={self.hausnummer!r}, " \
               f"plz={self.plz!r})"

    def __str__(self):
        if self.bezeichner and not self.is_home:
            return f"{self.bezeichner} - {self.strasse} {self.hausnummer}, {self.plz} {self.stadt}"
        else:
            return f"{self.strasse} {self.hausnummer}, {self.plz} {self.stadt}"


# wird ein neuer Assistent gespeichert bekommt er erstmal eine leere Adresse
# sein "home"
@receiver(post_save, sender=Assistent)
def create_adresse(sender, instance, created, **kwargs):
    if created:
        Adresse.objects.create(assistent=instance, is_home=True, bezeichner='Zu Hause')


