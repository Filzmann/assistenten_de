from django.contrib.auth.models import User
from django.db.models import ForeignKey, CASCADE, CharField
from assistenten.models import AbstractZeitraum
from assistenten.models.assistent import Assistent


class Urlaub(AbstractZeitraum):
    assistent = ForeignKey(Assistent, on_delete=CASCADE)
    status = CharField(max_length=10)

    def __repr__(self):
        return f"Urlaub({self.beginn!r}, " \
               f"-{self.ende!r}) "

    def __str__(self):
        return f"Urlaub({self.beginn!r}, " \
               f"-{self.ende!r}) "



