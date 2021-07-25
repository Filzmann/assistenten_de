from betterforms.multiform import MultiModelForm

from assistenten.forms.asn.asn_edit_schicht_form import AsnEditSchichtForm
from assistenten.forms.edit_as import AsnEditAsForm


class AsnCreateSchichtMultiForm(MultiModelForm):
    form_classes = {
        'schicht': AsnEditSchichtForm,
        'as_stammdaten': AsnEditAsForm,
    }


class AsnEditSchichtMultiForm(MultiModelForm):
    form_classes = {
        'schicht': AsnEditSchichtForm,
        'as_stammdaten': AsnEditAsForm,
    }
