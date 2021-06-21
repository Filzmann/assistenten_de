from datetime import datetime

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone

from assistenten.models import ASN


class Assistent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    vorname = models.CharField(max_length=30)
    email = models.CharField(max_length=30)
    einstellungsdatum = models.DateTimeField(default=timezone.now())

    asns = models.ManyToManyField(ASN, through='AssociationAsAsn', related_name='assistents')

    def get_absolute_url(self):
        return reverse('edit_as', kwargs={'pk': self.pk})

    def __repr__(self):
        return f"Assistent({self.name!r}, {self.vorname!r})"

    def __str__(self):
        return f"Assistent({self.name!r}, {self.vorname!r})"


@receiver(post_save, sender=User)
def create_assistent(sender, instance, created, **kwargs):
    if created:
        Assistent.objects.create(
            user=instance,
            email=instance.email,
            vorname=instance.first_name,
            name=instance.last_name
        )


@receiver(post_save, sender=User)
def save_assistent(sender, instance, **kwargs):
    instance.assistent.save()
