from betterforms.multiform import MultiModelForm

from assistenten.forms.edit_schicht import EditSchichtForm


class CreateSchichtMultiForm(MultiModelForm):
    form_classes = {
        'edit_schicht': EditSchichtForm,
    }


class EditSchichtMultiForm(MultiModelForm):
    form_classes = {
        'edit_schicht': EditSchichtForm,
    }