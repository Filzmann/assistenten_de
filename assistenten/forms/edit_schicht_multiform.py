from betterforms.multiform import MultiModelForm

from assistenten.forms.adresse import HomeForm
from assistenten.forms.edit_asn_stammdaten import EditAsnStammdatenForm
from assistenten.forms.edit_schicht_form import EditSchichtForm


class CreateSchichtMultiForm(MultiModelForm):
    form_classes = {
        'schicht': EditSchichtForm,
        'asn_stammdaten': EditAsnStammdatenForm,
        'asn_home': HomeForm,
    }


class EditSchichtMultiForm(MultiModelForm):
    form_classes = {
        'schicht': EditSchichtForm,
        'asn_stammdaten': EditAsnStammdatenForm,
        'asn_home': HomeForm,
    }
