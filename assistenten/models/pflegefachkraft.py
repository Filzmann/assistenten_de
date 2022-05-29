
from assistenten.models import AbstractPerson


class PFK(AbstractPerson):

    def __repr__(self):
        return f"{self.name!r}, {self.vorname!r})"

    def __str__(self):
        return f"{self.vorname} {self.name}"