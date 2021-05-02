from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import UpdateView, CreateView
from django.shortcuts import redirect
from assistenten.forms.edit_schicht_multiform import EditSchichtMultiForm, CreateSchichtMultiForm
from assistenten.models import Schicht


class CreateSchichtView(LoginRequiredMixin, CreateView):
    template_name = "assistenten/edit_schicht.html"
    form_class = CreateSchichtMultiForm
    model = Schicht
    success_url = reverse_lazy('index')

    def get_form_kwargs(self):
        kwargs = super(CreateSchichtView, self).get_form_kwargs()
        kwargs.update(instance={
            'schicht': self.object,

        })
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        schicht = form['edit_schicht'].save()
        assistent = self.request.user.assistent
        schicht.assistents.add(assistent)
        schicht.save()

        return redirect('edit_asn', pk=schicht.id)


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
