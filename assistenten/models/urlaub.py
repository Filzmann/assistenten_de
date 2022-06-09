from django.db import models
from assistenten.models import AU, AbstractCalendarEntry


class Urlaub(AbstractCalendarEntry):
    status = models.CharField(max_length=10)

    def __repr__(self):
        return f"Urlaub({self.beginn!r}, " \
               f"-{self.ende!r}) "

    def __str__(self):
        return f"Urlaub({self.beginn!r}, " \
               f"-{self.ende!r}) "



