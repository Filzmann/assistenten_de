from django.contrib.auth.models import User
from django.db import models


class PFK(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=30)
    vorname = models.CharField(max_length=30)
    email = models.CharField(max_length=30)

    def __repr__(self):
        return f"{self.name!r}, {self.vorname!r})"

    def __str__(self):
        return f"{self.vorname} {self.name}"