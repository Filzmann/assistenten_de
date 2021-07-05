from datetime import datetime

from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from guardian.conf import settings
from guardian.shortcuts import assign_perm
from assistenten.models import ASN


class Assistent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=30)
    vorname = models.CharField(max_length=30)
    email = models.CharField(max_length=30)
    einstellungsdatum = models.DateTimeField(default=timezone.now)
    asns = models.ManyToManyField(ASN, through='AssociationAsAsn', related_name='assistents')

    def get_absolute_url(self):
        return reverse('edit_as', kwargs={'pk': self.pk})

    def __repr__(self):
        return f"Assistent({self.name!r}, {self.vorname!r})"

    def __str__(self):
        return f"Assistent({self.name!r}, {self.vorname!r})"


@receiver(m2m_changed)
def signal_handler_when_user_is_added_or_removed_from_group(action, instance, pk_set, model, **kwargs):
    if model == Group:
        if action == 'post_add':
            # TODO: add logic
            user, groups = instance, pk_set
            if 1 in groups:
                if not hasattr(user, 'assistent'):
                    if user.username != settings.ANONYMOUS_USER_NAME:
                        assistent = Assistent.objects.create(
                            user=user,
                            email=user.email,
                            vorname=user.first_name,
                            name=user.last_name
                        )
                        assign_perm("change_user", user, user)
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
                    assign_perm("change_user", user, user)
                    assign_perm("change_asn", user, asn)

            # TODO Bei weiteren Nutzergruppen erweitern
        # handle as many actions as one needs
    # The following for loop prints every group that were
    # added/removed.
    # for pk in pk_set:
    #    group = Group.objects.get(id=pk)
    #    print(group)

