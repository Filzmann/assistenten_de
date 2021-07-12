from betterforms.multiform import MultiModelForm
from assistenten.forms.adresse import HomeForm
from assistenten.forms.edit_asn_feste_schichten import FesteSchichtenForm
from assistenten.forms.edit_asn_schicht_templates import SchichtTemplatesForm
from assistenten.forms.edit_asn_stammdaten import EditAsnStammdatenForm


class AsCreateAsnMultiForm(MultiModelForm):
    form_classes = {
        'asn_stammdaten': EditAsnStammdatenForm,
        'asn_adresse': HomeForm,

    }


class AsEditAsnMultiForm(MultiModelForm):
    form_classes = {
        'asn_stammdaten': EditAsnStammdatenForm,
        'asn_adresse': HomeForm,
        'asn_schicht_templates': SchichtTemplatesForm,
        'asn_feste_schicht': FesteSchichtenForm,
    }
