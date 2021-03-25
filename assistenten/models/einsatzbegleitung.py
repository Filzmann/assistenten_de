from django.db import models


class EB(models.Model):
    name = models.CharField(max_length=30)
    vorname = models.CharField(max_length=30)
    email = models.CharField(max_length=30)

    def __repr__(self):
        return f"{self.vorname} {self.name}"
