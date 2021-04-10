from betterforms.multiform import MultiModelForm
from assistenten.forms import EditAsForm
from assistenten.forms.adresse import HomeForm


class EditAsMultiForm(MultiModelForm):


    form_classes = {
        'assistent': EditAsForm,
        'adresse': HomeForm,
    }
