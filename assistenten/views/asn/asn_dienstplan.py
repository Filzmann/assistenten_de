from assistenten.views.abstract_dienstplan_view import AbstractDienstplanView


class AsnDienstplanView(AbstractDienstplanView):
    context_object_name = 'as_dienstplan_monat'
    template_name = 'assistenten/asn/show_dienstplan.html'

    def get_context_data(self, **kwargs):
        self.asn = self.request.user.assistenznehmer
        context = super(AsnDienstplanView, self).get_context_data(**kwargs)
        return context
