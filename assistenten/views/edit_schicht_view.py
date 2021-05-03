from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import UpdateView, CreateView
from django.shortcuts import redirect
from assistenten.forms.edit_schicht_multiform import EditSchichtMultiForm, CreateSchichtMultiForm
from assistenten.models import Schicht, Adresse, ASN


class CreateSchichtView(LoginRequiredMixin, CreateView):
    template_name = "assistenten/edit_schicht.html"
    form_class = CreateSchichtMultiForm
    model = Schicht
    success_url = reverse_lazy('index')

    def get_form_kwargs(self):
        kwargs = super(CreateSchichtView, self).get_form_kwargs()
        # wenn asn in POST select home-adresse für beginn und ende der schicht
        if self.request.method in ('POST', 'PUT'):
            if kwargs['data']['schicht-asn']:
                localPost = self.request.POST.copy()
                home_address_id = Adresse.objects.filter(
                    is_home=True).filter(
                    asn=ASN.objects.get(
                        id=kwargs['data']['schicht-asn']
                    )
                )[0].id
                localPost['schicht-beginn_adresse'] = home_address_id
                localPost['schicht-ende_adresse'] = home_address_id

                kwargs.update({
                    'data': localPost
                })

        kwargs.update(instance={
            'schicht': self.object,
        },
            request=self.request
        )
        return kwargs



    def form_valid(self, form):
        print('eeeeey')
        print(form)
        schicht = form['edit_schicht'].save()
        assistent = self.request.user.assistent
        schicht.assistents.add(assistent)
        # schicht.save()

        # return redirect('edit_asn', pk=schicht.id)


class EditSchichtView(LoginRequiredMixin, UpdateView):
    template_name = "assistenten/edit_schicht.html"
    form_class = EditSchichtMultiForm
    model = Schicht
    success_url = reverse_lazy('edit_schicht')

    # def get_form_kwargs(self):
    #     kwargs = super(CreateSchichtView, self).get_form_kwargs()
    #     kwargs.update(instance={
    #         'assistent': self.object,
    #         'adresse': self.object.adressen.all().filter(is_home=True)[0]
    #     })
    #     return kwargs

    def form_valid(self, form):
        schicht = form['edit_schicht'].save()
        assistent = self.request.user.assistent
        schicht.assistents.add(assistent)
        schicht.save()

        return redirect('edit_asn', pk=schicht.id)
