import googlemaps
from django.db import models
from django.utils import timezone

from assistenten.models import Adresse
from assistenten_de.settings import GOOGLE_API_KEY


class Weg(models.Model):
    entfernung = models.DecimalField(decimal_places=2, max_digits=5)
    dauer_in_minuten = models.IntegerField()
    adresse1 = models.ForeignKey(Adresse, on_delete=models.CASCADE, related_name='+')
    adresse2 = models.ForeignKey(Adresse, on_delete=models.CASCADE, related_name='+')

    def __repr__(self):
        return f"Adresse1={self.adresse1!r}, " \
               f"Adresse2={self.adresse2!r})"

    @classmethod
    def get_weg_id(cls, adresse1, adresse2):
        # prüfen ob weg in Modell wege vorhanden
        wege = cls.objects.filter(adresse1=adresse1, adresse2=adresse2) | Weg.objects.filter(adresse1=adresse2,
                                                                                             adresse2=adresse1)
        # print(wege)
        if wege:
            return wege[0].pk
        else:
            weg = cls.create(adresse1, adresse2)
            if weg:
                return weg
            else:
                return False
        # bei Bedarf insert, werte für Weg + Zeit per google api ermitteln

    @classmethod
    def create(cls, adresse1, adresse2):
        gmaps = googlemaps.Client(key=GOOGLE_API_KEY)

        adresse1_string = \
            adresse1.strasse + ' ' \
            + adresse1.hausnummer + ', ' \
            + adresse1.plz + ' ' \
            + adresse1.stadt

        adresse2_string = \
            adresse2.strasse + ' ' \
            + adresse2.hausnummer + ', ' \
            + adresse2.plz + ' ' \
            + adresse2.stadt

        directions_result = gmaps.directions(adresse1_string,
                                             adresse2_string,
                                             mode="transit",
                                             departure_time=timezone.now())

        if directions_result:
            distance = directions_result[0]['legs'][0]['distance']['value'] / 1000
            duration = round(directions_result[0]['legs'][0]['duration']['value'] / 60 + 0.5)

            weg = cls(adresse1=adresse1, adresse2=adresse2, entfernung=distance, dauer_in_minuten=duration)
            weg.save()

            return weg.pk
        else:
            return False
