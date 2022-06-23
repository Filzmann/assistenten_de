from assistenten.models import AbstractAbsence


class AU(AbstractAbsence):
    def __str__(self):
        return f"AU {self.assistent}: {self.beginn} - {self.ende} "
