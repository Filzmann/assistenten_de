from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils.datetime_safe import datetime
from django.views.generic import UpdateView, CreateView, DeleteView
from django.shortcuts import redirect
from assistenten.forms.edit_schicht_multiform import AsnCreateSchichtMultiForm, AsnEditSchichtMultiForm
from assistenten.functions.person_functions import get_address
from assistenten.models import Schicht, Adresse, ASN


# TODO beim Eintragen von Schichten über den Jahreswechsel werden daten falsch übernommen.
# Vermutlich im Javascript zur Templateübernahme


class AsnCreateSchichtView(LoginRequiredMixin, CreateView):
    template_name = "assistenten/asn_edit_schicht.html"
    form_class = AsnCreateSchichtMultiForm
    model = Schicht
    success_url = reverse_lazy('index')

    def get_form_kwargs(self):
        print('a')

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
        print(kwargs)
        if self.request.method in ('POST', 'PUT'):
            if 'schicht-assistent' in kwargs['data']:
                local_post = self.request.POST.copy()
                if not kwargs['data']['schicht-assistent'] == '':
                    home_address_id = get_address(asn=self.request.user.assistenznehmer, is_home=True)
                    print('--------------------------------')
                    local_post['schicht-beginn_adresse'] = home_address_id
                    local_post['schicht-ende_adresse'] = home_address_id

                # local kwargs wird ergänzt und für einige keys überschrieben,
                # damit alle vorhandenen Daten gespeichert werden können
                for key in local_post:
                    local_kwargs_data[key] = local_post[key]

        kwargs.update(data=local_kwargs_data)

        # print(kwargs)
        return kwargs

    def form_valid(self, form):
        schicht = form['schicht'].save(commit=False)
        if not hasattr(schicht, 'assistent'):
            schicht.assistent = form['as_stammdaten'].save()
            schicht.assistent.asn.add(self.request.user.asn)
            # print(asn_home)
            # schicht.beginn_adresse = as_home
            # schicht.ende_adresse = asn_home

        asn = self.request.user.assistenznehmer

        schicht.asn = asn
        schicht.beginn_adresse = get_address(asn=asn, is_home=True)
        schicht.ende_adresse = get_address(asn=asn, is_home=True)

        schicht.save()
        return redirect('as_edit_schicht', pk=schicht.id)


class AsnEditSchichtView(LoginRequiredMixin, UpdateView):
    template_name = "assistenten/as_edit_schicht.html"
    form_class = AsnEditSchichtMultiForm
    model = Schicht
    success_url = reverse_lazy('edit_schicht')

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
            if 'schicht-asn' in kwargs['data']:
                home_address_id = Adresse.objects.filter(
                    is_home=True).filter(
                    asn=ASN.objects.get(
                        id=kwargs['data']['schicht-asn']
                    )
                )[0].id
                local_post['schicht-beginn_adresse'] = home_address_id
                local_post['schicht-ende_adresse'] = home_address_id

                # local kwargs wird ergänzt und für einige keys überschrieben,
                # damit alle vorhandenen Daten gespeichert werden können
                for key in local_post:
                    local_kwargs_data[key] = local_post[key]

        if local_kwargs_data:
            kwargs.update(
                data=local_kwargs_data
            )
        return kwargs

    def form_valid(self, form):
        schicht = form['schicht'].save(commit=False)
        schicht.save()

        if 'just_save' in self.request.POST:
            return redirect('as_schicht_tabelle', year=schicht.beginn.year, month=schicht.beginn.month)
        elif 'save_and_new' in self.request.POST:
            return redirect('as_create_schicht', y=schicht.beginn.year, m=schicht.beginn.month, d=schicht.beginn.day)
        else:
            return redirect('as_edit_schicht', pk=schicht.id)


class DeleteSchichtView(LoginRequiredMixin, DeleteView):
    model = Schicht
    success_url = reverse_lazy('as_schicht_tabelle')

    def get_success_url(self):
        usergroup = self.request.user.groups.values_list('name', flat=True).first()
        if usergroup == "Assistenten":
            return reverse_lazy('as_schicht_tabelle')
        elif usergroup == "Assistenznehmer":
            return reverse_lazy('asn_dienstplan')
