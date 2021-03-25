from django.db import models


class PFK(models.Model):
    name = models.CharField(max_length=30)
    vorname = models.CharField(max_length=30)
    email = models.CharField(max_length=30)

    def __repr__(self):
        return f"{self.name!r}, {self.vorname!r})"
