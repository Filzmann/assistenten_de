from django.db import models


class Lohn(models.Model):
    erfahrungsstufe = models.IntegerField()
    gueltig_ab = models.DateTimeField()
    eingruppierung = models.IntegerField()
    grundlohn = models.DecimalField(decimal_places=4, max_digits=4)
    nacht_zuschlag = models.DecimalField(decimal_places=4, max_digits=4)
    samstag_zuschlag = models.DecimalField(decimal_places=4, max_digits=4)
    sonntag_zuschlag = models.DecimalField(decimal_places=4, max_digits=4)
    feiertag_zuschlag = models.DecimalField(decimal_places=4, max_digits=4)
    wechselschicht_zuschlag = models.DecimalField(decimal_places=4, max_digits=4)
    orga_zuschlag = models.DecimalField(decimal_places=4, max_digits=4)
    ueberstunden_zuschlag = models.DecimalField(decimal_places=4, max_digits=4)
    hl_abend_zuschlag = models.DecimalField(decimal_places=4, max_digits=4)
    silvester_zuschlag = models.DecimalField(decimal_places=4, max_digits=4)
