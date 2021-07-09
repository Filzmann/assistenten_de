from assistenten.models import SchichtTemplate, FesteSchicht


def get_schicht_templates(asn):
# alle schicht_templates des asn
    schicht_template_liste = []
    schicht_templates = SchichtTemplate.objects.filter(
        asn=asn.id)
    for schicht_template in schicht_templates:
        schicht_template_liste.append({
            'id': schicht_template.id,
            'bezeichner': schicht_template.bezeichner,
            'beginn': schicht_template.beginn.strftime("%H:%M"),
            'ende': schicht_template.ende.strftime("%H:%M"),
        })

    return schicht_templates


def get_feste_schichten(asn=None, assistent=None):
    # alle festen Schichten des asn
    feste_schichten_liste = []
    feste_schichten = FesteSchicht.objects

    if asn:
        feste_schichten = feste_schichten.filter(asn=asn.id)
    if assistent:
        feste_schichten = feste_schichten.filter(assistent=assistent.id)

    wtage = {'0': 'Mo', '1': 'Di', '2': 'Mi', '3': 'Do', '4': 'Fr', '5': 'Sa', '6': 'So'}

    for feste_schicht in feste_schichten:
        feste_schichten_liste.append({
            'id': feste_schicht.id,
            'wochentag': wtage[feste_schicht.wochentag],
            'beginn': feste_schicht.beginn.strftime("%H:%M"),
            'ende': feste_schicht.ende.strftime("%H:%M"),
        })
    return feste_schichten_liste