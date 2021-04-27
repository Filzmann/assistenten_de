from betterforms.multiform import MultiModelForm
from assistenten.forms.edit_asn_stammdaten import EditAsnStammdatenForm

from assistenten.forms.edit_schicht import EditSchichtForm


class CreateSchichtMultiForm(MultiModelForm):
    form_classes = {
        'edit_schicht': EditSchichtForm,
        'edit_asn_stammdaten': EditAsnStammdatenForm,
    }


class EditSchichtMultiForm(MultiModelForm):
    form_classes = {
        'edit_schicht': EditSchichtForm,
    }
