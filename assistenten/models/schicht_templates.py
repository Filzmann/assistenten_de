from django.db import models
from assistenten.models.assistenznehmer import ASN


class SchichtTemplate(models.Model):
    # relationships
    asn = models.ForeignKey(ASN, on_delete=models.CASCADE)

    # extra data
    beginn = models.TimeField()
    ende = models.TimeField()
    bezeichner = models.CharField(max_length=30)

    @classmethod
    def get_by_asn(cls, asn, order_by=False):
        # alle schicht_templates des asn
        schicht_template_liste = []
        schicht_templates = cls.objects.filter(
            asn=asn.id)
        if order_by:
            schicht_templates = schicht_templates.order_by(order_by)
        for schicht_template in schicht_templates:
            schicht_template_liste.append({
                'id': schicht_template.id,
                'bezeichner': schicht_template.bezeichner,
                'beginn': schicht_template.beginn,
                'ende': schicht_template.ende,
            })

        return schicht_templates

    def __repr__(self):
        return f"Template({self.bezeichner!r}, {self.beginn!r} - {self.ende!r})"

    def __str__(self):
        return f"{self.bezeichner}, {self.beginn.strftime('%H:%M')} - {self.ende.strftime('%H:%M')}"


