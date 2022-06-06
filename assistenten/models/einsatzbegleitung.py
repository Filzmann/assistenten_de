from assistenten.models import AbstractMitarbeiter


class EB(AbstractMitarbeiter):

    def __repr__(self):
        return f"{self.vorname} {self.name}"

    def __str__(self):
        return f"{self.vorname} {self.name}"
