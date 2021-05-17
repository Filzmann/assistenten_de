from django.db import models


class Lohn(models.Model):
    erfahrungsstufe = models.IntegerField()
    gueltig_ab = models.DateTimeField()
    eingruppierung = models.IntegerField()
    grundlohn = models.DecimalField(decimal_places=2, max_digits=5)
    kurzfristig_zuschlag_prozent = models.DecimalField(decimal_places=2, max_digits=5, default=20)
    nacht_zuschlag = models.DecimalField(decimal_places=2, max_digits=5)
    samstag_zuschlag = models.DecimalField(decimal_places=2, max_digits=5)
    sonntag_zuschlag = models.DecimalField(decimal_places=2, max_digits=5)
    feiertag_zuschlag = models.DecimalField(decimal_places=2, max_digits=5)
    wechselschicht_zuschlag = models.DecimalField(decimal_places=2, max_digits=5)
    orga_zuschlag = models.DecimalField(decimal_places=2, max_digits=5)
    ueberstunden_zuschlag = models.DecimalField(decimal_places=2, max_digits=5)
    hl_abend_zuschlag = models.DecimalField(decimal_places=2, max_digits=5)
    silvester_zuschlag = models.DecimalField(decimal_places=2, max_digits=5)

    def __repr__(self):
        return f"Lohn( gültig ab: {self.gueltig_ab!r}, EG {self.eingruppierung!r} , Stufe {self.erfahrungsstufe!r} )"

    def __str__(self):
        return f"Lohn( gültig ab: {self.gueltig_ab!r}, EG {self.eingruppierung!r} , Stufe {self.erfahrungsstufe!r} )"
