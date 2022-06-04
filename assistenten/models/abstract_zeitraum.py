from datetime import timedelta
from django.db import models
from django.utils import timezone
from django.utils.datetime_safe import datetime, time

from assistenten.functions.calendar_functions import get_duration


class AbstractZeitraum(models.Model):
    beginn = models.DateTimeField()
    ende = models.DateTimeField()

    class Meta:
        abstract = True

    def clone(self):
        """Returns a clone of this instance."""

        clone = self.__class__()
        for f in self.__class__._meta.fields:
            setattr(clone, f.attname, getattr(self, f.attname))

        return clone


    @property
    def stunden(self):
        return get_duration(self.beginn, self.ende, "minutes") / 60

    def check_mehrtaegig(self):
        # wenn schicht um 0 uhr endet, ist es noch der alte Tag
        if self.ende.hour == 0 and self.ende.minute == 0:
            ende = (self.ende - timedelta(days=1)).date()
        else:
            ende = self.ende.date()

        if self.beginn.date() == ende:
            return False
        else:
            return True

    def split_by_null_uhr(self):
        ausgabe = []
        rest = self.clone()
        while rest.check_mehrtaegig():
            out = rest.clone()
            rest.beginn = timezone.make_aware(
                datetime.combine(rest.beginn.date() + timedelta(days=1),
                                 time(0, 0)
                                 )
            )
            out.ende = rest.beginn
            ausgabe.append(out)
        if rest.stunden > 0:
            ausgabe.append(rest)
        return ausgabe
