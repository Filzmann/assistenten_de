from django.db.models import CharField, ForeignKey, CASCADE
from assistenten.models import EB, PFK, AbstractPerson


class ASN(AbstractPerson):
    kuerzel = CharField(max_length=30)
    einsatzbuero = CharField(max_length=30)

    einsatzbegleitung = ForeignKey(EB, on_delete=CASCADE, related_name='asns', null=True)
    pflegefachkraft = ForeignKey(PFK, on_delete=CASCADE, related_name='asns', null=True)

    def __repr__(self):
        return f"ASN(Kürzel={self.kuerzel!r}, Name={self.name!r}, Vorname={self.vorname!r})"

    def __str__(self):
        return f"{self.kuerzel} - {self.name}, {self.vorname}"
