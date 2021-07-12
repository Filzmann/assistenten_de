from betterforms.multiform import MultiModelForm
from assistenten.forms.adresse import HomeForm
from assistenten.forms.edit_asn_schicht_templates import SchichtTemplatesForm
from assistenten.forms.edit_asn_stammdaten import EditAsnStammdatenForm


class AsnEditAsnMultiForm(MultiModelForm):
    form_classes = {
        'asn': EditAsnStammdatenForm,
        'adresse': HomeForm,
        'asn_schicht_templates': SchichtTemplatesForm,
    }
