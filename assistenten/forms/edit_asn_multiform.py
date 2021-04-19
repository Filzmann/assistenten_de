from betterforms.multiform import MultiModelForm
from assistenten.forms.adresse import HomeForm
from assistenten.forms.edit_asn_feste_schichten import FesteSchichtenForm
from assistenten.forms.edit_asn_schicht_templates import SchichtTemplatesForm
from assistenten.forms.edit_asn_stammdaten import EditAsnStammdatenForm


class CreateAsnMultiForm(MultiModelForm):
    form_classes = {
        'asn_stammdaten': EditAsnStammdatenForm,
        'asn_adresse': HomeForm
    }


class EditAsnMultiForm(MultiModelForm):
    form_classes = {
        'asn_stammdaten': EditAsnStammdatenForm,
        'asn_adresse': HomeForm,
        'asn_feste_schicht': FesteSchichtenForm,
        'asn_schicht_templates': SchichtTemplatesForm,
    }
