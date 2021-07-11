from betterforms.multiform import MultiModelForm
from assistenten.forms import EditAsForm
from assistenten.forms.adresse import HomeForm
from assistenten.forms.edit_as import AsnEditAsForm
from assistenten.forms.edit_asn_feste_schichten import FesteSchichtenForm



class AsnCreateAsMultiForm(MultiModelForm):
    form_classes = {
        'as_stammdaten': AsnEditAsForm,
        'asn_adresse': HomeForm,
    }


class AsnEditAsMultiForm(MultiModelForm):
    form_classes = {
        'as_stammdaten': AsnEditAsForm,
        'as_adresse': HomeForm,
        'as_feste_schicht': FesteSchichtenForm,
    }
