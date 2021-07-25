from betterforms.multiform import MultiModelForm

from assistenten.forms.adresse import HomeForm
from assistenten.forms.assistent.as_edit_schicht_form import AsEditSchichtForm
from assistenten.forms.edit_asn_stammdaten import EditAsnStammdatenForm


class AsCreateSchichtMultiForm(MultiModelForm):
    form_classes = {
        'schicht': AsEditSchichtForm,
        'asn_stammdaten': EditAsnStammdatenForm,
        'asn_home': HomeForm,
    }


class AsEditSchichtMultiForm(MultiModelForm):
    form_classes = {
        'schicht': AsEditSchichtForm,
        'asn_stammdaten': EditAsnStammdatenForm,
        'asn_home': HomeForm,
    }