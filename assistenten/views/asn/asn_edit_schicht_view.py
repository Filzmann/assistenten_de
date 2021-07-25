from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils.datetime_safe import datetime
from django.views.generic import UpdateView, CreateView, DeleteView
from django.shortcuts import redirect
from guardian.shortcuts import assign_perm
from assistenten.forms.asn.asn_edit_schicht_multiform import AsnCreateSchichtMultiForm, AsnEditSchichtMultiForm
from assistenten.functions.person_functions import get_address
from assistenten.models import Schicht


class AsnCreateSchichtView(LoginRequiredMixin, CreateView):
    template_name = "assistenten/asn/asn_edit_schicht.html"
    form_class = AsnCreateSchichtMultiForm
    model = Schicht
    success_url = reverse_lazy('index')

    def get_form_kwargs(self):
        kwargs = super(AsnCreateSchichtView, self).get_form_kwargs()
        # übergebe den request in die kwargs, damit er im Form verfügbar ist.
        kwargs.update({'request': self.request})
        # haben wir schon daten im Objekt? dann kommen diese in die kwargs
        if self.object:
            kwargs.update(
                instance={'schicht': self.object, },
            )
        local_kwargs_data = kwargs['data'].copy() if 'data' in kwargs else {}

        # wenn wir von der schichttabelle oder saveAndNew kommen, wird ein datum übergeben.
        # dieses wird in in die Felder für Beginn und Ende der Schicht eingefügt.
        if 'y' in self.kwargs:
            beginnende = str(self.kwargs['d']).zfill(2) + '.' \
                         + str(self.kwargs['m']).zfill(2) + '.' \
                         + self.kwargs['y'] + ' ' \
                         + datetime.now().strftime('%H:%M')
            local_kwargs_data['schicht-beginn'] = beginnende
            local_kwargs_data['schicht-ende'] = beginnende

        # wenn asn in POST select home-adresse für beginn und ende der schicht

        if self.request.method in ('POST', 'PUT'):
            local_post = self.request.POST.copy()
            home_address_id = get_address(asn=self.request.user.assistenznehmer, is_home=True).first()
            local_post['schicht-beginn_adresse'] = home_address_id
            local_post['schicht-ende_adresse'] = home_address_id
            # local kwargs wird ergänzt und für einige keys überschrieben,
            # damit alle vorhandenen Daten gespeichert werden können
            for key in local_post:
                local_kwargs_data[key] = local_post[key]

        kwargs.update(data=local_kwargs_data)
        return kwargs

    def form_valid(self, form):

        schicht = form['schicht'].save(commit=False)
        if not hasattr(schicht, 'assistent'):
            schicht.assistent = form['as_stammdaten'].save()
            assign_perm("change_assistent", self.request.user, schicht.assistent)
            assign_perm("view_assistent", self.request.user, schicht.assistent)

        schicht.asn = self.request.user.assistenznehmer

        schicht.beginn_adresse = get_address(asn=schicht.asn, is_home=True).first()
        schicht.ende_adresse = get_address(asn=schicht.asn, is_home=True).first()
        schicht.save()
        return redirect('asn_edit_schicht', pk=schicht.id)


class AsnEditSchichtView(LoginRequiredMixin, UpdateView):
    template_name = "assistenten/asn/asn_edit_schicht.html"
    form_class = AsnEditSchichtMultiForm
    model = Schicht
    success_url = reverse_lazy('asn_edit_schicht')

    def get_form_kwargs(self):
        kwargs = super(AsnEditSchichtView, self).get_form_kwargs()

        # übergebe den request in die kwargs, damit er im Form verfügbar ist.
        kwargs.update({'request': self.request})
        # haben wir schon daten im Objekt? dann kommen diese in die kwargs

        if self.object:
            kwargs.update(
                instance={'schicht': self.object, },
            )
        local_kwargs_data = kwargs['data'].copy() if 'data' in kwargs else {}

        # wenn asn in POST select home-adresse für beginn und ende der schicht
        if self.request.method in ('POST', 'PUT'):
            local_post = self.request.POST.copy()
            home_address = get_address(asn=self.request.user.assistenznehmer, is_home=True).first()
            local_post['schicht-beginn_adresse'] = home_address
            local_post['schicht-ende_adresse'] = home_address
            # local kwargs wird ergänzt und für einige keys überschrieben,
            # damit alle vorhandenen Daten gespeichert werden können
            for key in local_post:
                local_kwargs_data[key] = local_post[key]
            kwargs.update(data=local_kwargs_data)
        return kwargs

    def form_valid(self, form):
        schicht = form['schicht'].save()
        if 'just_save' in self.request.POST:
            return redirect('asn_dienstplan', year=schicht.beginn.year, month=schicht.beginn.month)
        elif 'save_and_new' in self.request.POST:
            return redirect('asn_create_schicht', y=schicht.beginn.year, m=schicht.beginn.month, d=schicht.beginn.day)
        else:
            return redirect('asn_edit_schicht', pk=schicht.id)


class DeleteSchichtView(LoginRequiredMixin, DeleteView):
    model = Schicht
    success_url = reverse_lazy('as_schicht_tabelle')

    def get_success_url(self):
        usergroup = self.request.user.groups.values_list('name', flat=True).first()
        if usergroup == "Assistenten":
            return reverse_lazy('as_schicht_tabelle')
        elif usergroup == "Assistenznehmer":
            return reverse_lazy('asn_dienstplan')
