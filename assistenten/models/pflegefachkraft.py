from django.db import models

from assistenten.models import AbstractMitarbeiter


class PFK(AbstractMitarbeiter):

    def __repr__(self):
        return f"{self.name!r}, {self.vorname!r})"

    def __str__(self):
        return f"{self.vorname} {self.name}"