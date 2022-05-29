from django.db.models import ForeignKey, CASCADE
from assistenten.models import AbstractZeitraum, Assistent


class AU(AbstractZeitraum):
    assistent = ForeignKey(Assistent, on_delete=CASCADE)

