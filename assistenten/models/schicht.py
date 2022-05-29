from datetime import timedelta

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.datetime_safe import datetime
from django.utils.timezone import localtime
from assistenten.models import Adresse, Urlaub, AU, AbstractZeitraum
from assistenten.models.assistent import Assistent
from assistenten.models.assistenznehmer import ASN


class Schicht(AbstractZeitraum):
    asn = models.ForeignKey(ASN, on_delete=models.CASCADE)
    assistent = models.ForeignKey(Assistent, on_delete=models.CASCADE)
    ist_kurzfristig = models.BooleanField(default=0)
    ist_ausfallgeld = models.BooleanField(default=0)
    ist_assistententreffen = models.BooleanField(default=0)
    ist_pcg = models.BooleanField(default=0)
    ist_schulung = models.BooleanField(default=0)
    beginn_adresse = models.ForeignKey(Adresse, on_delete=models.CASCADE, related_name='+')
    ende_adresse = models.ForeignKey(Adresse, on_delete=models.CASCADE, related_name='+')

    def __repr__(self):
        return f"Schicht( Beginn: {self.beginn!r}, Ende: {self.ende!r}, ASN: {self.asn!r}  - AS: {self.assistent})"

    def __str__(self):
        return f"Schicht({self.beginn} - {self.ende} - ASN: {self.asn} - AS: {self.assistent}"


# Lösche Schicht, wenn Urlaub gespeichert wird.
@receiver(post_save, sender=Urlaub)
def delete_urlaubsschicht(sender, instance, created, **kwargs):
    time = localtime().replace(hour=0, minute=0, second=0, microsecond=0)
    # DELETE-query
    Schicht.objects.filter(
        beginn__range=(
            datetime.combine(instance.beginn, time),
            datetime.combine(instance.ende + timedelta(days=1), time)
        )
    ).filter(assistent=instance.assistent).delete() | Schicht.objects.filter(
        ende__range=(
            datetime.combine(instance.beginn, time),
            datetime.combine(instance.ende + timedelta(days=1), time)
        )
    ).filter(assistent=instance.assistent).delete()


# Lösche Schicht, wenn AU gespeichert wird.
@receiver(post_save, sender=AU)
def delete_urlaubsschicht(sender, instance, created, **kwargs):
    time = localtime().replace(hour=0, minute=0, second=0, microsecond=0)
    # DELETE-query
    Schicht.objects.filter(
        beginn__range=(
            datetime.combine(instance.beginn, time),
            datetime.combine(instance.ende + timedelta(days=1), time)
        )
    ).filter(assistent=instance.assistent).delete()
    Schicht.objects.filter(
        ende__range=(
            datetime.combine(instance.beginn, time),
            datetime.combine(instance.ende + timedelta(days=1), time)
        )
    ).filter(assistent=instance.assistent).delete()
