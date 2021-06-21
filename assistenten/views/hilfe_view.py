from django.views.generic import TemplateView


class HilfeView(TemplateView):
    template_name = "assistenten/hilfe.html"
