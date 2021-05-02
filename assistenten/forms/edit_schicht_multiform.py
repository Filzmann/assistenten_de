from betterforms.multiform import MultiModelForm
from assistenten.forms.edit_asn_stammdaten import EditAsnStammdatenForm
from assistenten.forms.edit_schicht import EditSchichtForm


class CreateSchichtMultiForm(MultiModelForm):
    form_classes = {
        'schicht': EditSchichtForm,
        'asn_stammdaten': EditAsnStammdatenForm,
    }

    def __init__(self, *args, **kwargs):
        """ Grants access to the request object for each instance object so that only members of the current user
                are given as options"""
        self.request = kwargs.pop('request')
        for inst in kwargs['instance']:
            if kwargs['instance'][inst]:
                kwargs['instance'][inst]['request'] = self.request
            else:
                kwargs['instance'][inst] = {'request': self.request}
        super(CreateSchichtMultiForm, self).__init__(*args, **kwargs)



class EditSchichtMultiForm(MultiModelForm):
    form_classes = {
        'schicht': EditSchichtForm,
    }
