from django.db.models import Model, DateTimeField


class AbstractZeitraum(Model):
    beginn = DateTimeField()
    ende = DateTimeField()

    class Meta:
        abstract = True
