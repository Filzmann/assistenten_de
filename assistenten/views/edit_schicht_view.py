from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils.datetime_safe import datetime
from django.views.generic import UpdateView, CreateView, DeleteView
from django.shortcuts import redirect
from guardian.shortcuts import assign_perm
from assistenten.forms.asn.asn_edit_schicht_multiform import AsnCreateSchichtMultiForm, AsnEditSchichtMultiForm
from assistenten.functions.person_functions import get_address
from assistenten.models import Schicht, ASN, Assistent


class CreateSchichtView(LoginRequiredMixin, CreateView):
    model = Schicht
    success_url = reverse_lazy('index')
    asn = None
    assistent = None

    def get_form_kwargs(self):
        kwargs = super(CreateSchichtView, self).get_form_kwargs()
        # übergebe den request in die kwargs, damit er im Form verfügbar ist.
        kwargs.update({'request': self.request})

        # haben wir schon daten im Objekt? dann kommen diese in die kwargs
        if self.object:
            kwargs.update(
                instance={'schicht': self.object, },
            )
        if 'data' in kwargs:
            local_kwargs_data = kwargs['data'].copy()
        else:
            local_kwargs_data = {}

        if 'schicht-asn' in local_kwargs_data:
            self.asn=ASN.objects.get(id=local_kwargs_data['schicht-asn'])
        if 'schicht-assistent' in local_kwargs_data:
            self.assistent = Assistent.objects.get(id=local_kwargs_data['schicht-assistent'])
        # wenn wir von der schichttabelle oder saveAndNew kommen, wird ein datum übergeben.
        # dieses wird in in die Felder für Beginn und Ende der Schicht eingefügt.
        if 'y' in self.kwargs:
            beginnende = str(self.kwargs['d']).zfill(2) + '.' \
                         + str(self.kwargs['m']).zfill(2) + '.' \
                         + self.kwargs['y'] + ' ' \
                         + datetime.now().strftime('%H:%M')
            local_kwargs_data['schicht-beginn'] = beginnende
            local_kwargs_data['schicht-ende'] = beginnende

        local_post = self.request.POST.copy()
        if self.asn:
            home_address_id = get_address(asn=self.asn, is_home=True).first()
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
        if not hasattr(schicht, 'assistent') and 'as_stammdaten' in form:
            schicht.assistent = form['as_stammdaten'].save()
            assign_perm("change_assistent", self.request.user, schicht.assistent)
            assign_perm("view_assistent", self.request.user, schicht.assistent)

        if not hasattr(schicht, 'asn') and 'asn_stammdaten' in form:
            schicht.asn = form['asn_stammdaten'].save()
            schicht.asn.assistents.add(self.assistent)
            asn_home = form['asn_home'].save(commit=False)

            asn_home.asn = schicht.asn
            asn_home.is_home = True
            asn_home.save()

            assign_perm("change_asn", self.request.user, schicht.asn)
            assign_perm("view_asn", self.request.user, schicht.asn)

        if not schicht.asn:
            schicht.asn = self.asn
        if not schicht.assistent:
            schicht.assistent = self.assistent


        schicht.beginn_adresse = get_address(asn=schicht.asn, is_home=True).first()
        schicht.ende_adresse = get_address(asn=schicht.asn, is_home=True).first()
        schicht.save()
        return self.get_success_url(schicht_id=schicht.id)

    def get_success_url(self, kwargs):
        redirect('asn_edit_schicht', pk=kwargs['schicht_id'])


class EditSchichtView(LoginRequiredMixin, UpdateView):
    model = Schicht
    success_url = reverse_lazy('eb_edit_schicht')
    asn = None
    assistent = None

    def get_form_kwargs(self):
        kwargs = super(EditSchichtView, self).get_form_kwargs()

        # übergebe den request in die kwargs, damit er im Form verfügbar ist.
        kwargs.update({'request': self.request})
        if self.object:
            kwargs.update(
                instance={'schicht': self.object, },
            )

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
    success_url = reverse_lazy('index')

