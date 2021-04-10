from betterforms.forms import Fieldset
from betterforms.multiform import MultiModelForm
from assistenten.forms.adresse import HomeForm
from assistenten.forms.edit_asn_stammdaten import EditAsnStammdatenForm


class EditAsnMultiForm(MultiModelForm):
    class Meta:
        fieldsets = (
            Fieldset('info', fields=('name',
                                     'vorname',
                                     'email',
                                     'einstellungsdatum'), legend='Stammdaten'),
        )

    form_classes = {
        'asn_stammdaten': EditAsnStammdatenForm,
        'asn_adresse': HomeForm,
    }
