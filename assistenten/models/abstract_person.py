from django.contrib.auth.models import User
from django.db import models


class AbstractPerson(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=30)
    vorname = models.CharField(max_length=30)
    email = models.CharField(max_length=30)

    class Meta:
        abstract = True

