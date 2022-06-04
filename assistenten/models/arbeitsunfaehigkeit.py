from django.db import models
from assistenten.models import Assistent, AbstractZeitraum


class AU(AbstractZeitraum):
    assistent = models.ForeignKey(Assistent, on_delete=models.CASCADE)


