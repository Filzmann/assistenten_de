from assistenten.models.abstract_person import AbstractPerson


class EB(AbstractPerson):

    def __repr__(self):
        return f"{self.vorname} {self.name}"

    def __str__(self):
        return f"{self.vorname} {self.name}"
