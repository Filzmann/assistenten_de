from betterforms.multiform import MultiModelForm
from assistenten.forms.adresse import HomeForm
from assistenten.forms.edit_asn_stammdaten import EditAsnStammdatenForm


class EditAsnMultiForm(MultiModelForm):
    form_classes = {
        'asn_stammdaten': EditAsnStammdatenForm,
        'asn_adresse': HomeForm,
    }
