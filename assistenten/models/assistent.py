from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.urls import reverse
from guardian.conf import settings
from guardian.shortcuts import assign_perm
from assistenten.models import ASN, Lohn
from assistenten.models.abstract_person import AbstractMitarbeiter


class Assistent(AbstractMitarbeiter):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    asns = models.ManyToManyField(ASN, through='AssociationAsAsn', related_name='assistents')

    def get_absolute_url(self):
        return reverse('as_edit_as', kwargs={'pk': self.pk})

    def lohn(self, datum):
        erfahrungsstufe = self.erfahrungsstufe(datum)
        lohn = Lohn.objects.filter(erfahrungsstufe=erfahrungsstufe).filter(
            gueltig_ab__lte=datum).filter(
            eingruppierung=5
        ).order_by('gueltig_ab')[0:1].get()
        if lohn:
            return lohn
        return False

    def __repr__(self):
        return f"{self.name}, {self.vorname} (AS)"

    def __str__(self):
        return f"{self.name}, {self.vorname} (AS)"


@receiver(m2m_changed)
def signal_handler_when_user_is_added_or_removed_from_group(action, instance, pk_set, model, **kwargs):
    user, groups = instance, pk_set
    if model == Group and user.username != settings.ANONYMOUS_USER_NAME:
        if action == 'post_add':
            if 1 in groups:
                if not hasattr(user, 'assistent'):
                    assistent = Assistent.objects.create(
                        user=user,
                        email=user.email,
                        vorname=user.first_name,
                        name=user.last_name
                    )
                else:
                    assistent = user.assistent
                if not user.has_perm("change_user", user):
                    assign_perm("change_user", user, user)
                if not user.has_perm("change_assistent", assistent):
                    assign_perm("change_assistent", user, assistent)
            if 2 in groups:
                if not hasattr(user, 'assistenznehmer'):
                    asn = ASN.objects.create(
                        user=user,
                        email=user.email,
                        vorname=user.first_name,
                        name=user.last_name,
                        kuerzel=user.username
                    )
                else:
                    asn = user.assistenznehmer
                if not user.has_perm("change_user", user):
                    assign_perm("change_user", user, user)
                if not user.has_perm("change_asn", asn):
                    assign_perm("change_asn", user, asn)

            # TODO Bei weiteren Nutzergruppen erweitern
