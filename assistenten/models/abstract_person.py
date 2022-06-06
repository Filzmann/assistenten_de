from django.db import models
from django.utils import timezone
from assistenten.functions.calendar_functions import get_duration


class AbstractPerson(models.Model):
    name = models.CharField(max_length=30)
    vorname = models.CharField(max_length=30)
    email = models.CharField(max_length=30)


    class Meta:
        abstract = True


class AbstractMitarbeiter(AbstractPerson):
    einstellungsdatum = models.DateTimeField(default=timezone.now)

    class Meta:
        abstract = True

    def erfahrungsstufe(self, datum=timezone.now()):
        delta = get_duration(self.einstellungsdatum, datum, 'years')
        # einstieg mit 1
        # nach 1 Jahr insgesamt 2
        # nach 3 jahren insgesamt 3
        # nach 6 jahren insg. 4
        # nach 10 Jahren insg. 5
        # nach 15 Jahren insg. 6
        if delta == 0:
            return 1
        elif 1 <= delta < 3:
            return 2
        elif 3 <= delta < 6:
            return 3
        elif 6 <= delta < 10:
            return 4
        elif 10 <= delta < 15:
            return 5
        else:
            return 6
