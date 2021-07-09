from django.views import View
from django.http import HttpResponseRedirect


class GroupBasedRedirector(View):

    def get(self, request, *args, **kwargs):
        # usergroup = None
        usergroup = self.request.user.groups.values_list('name', flat=True).first()
        if not usergroup:
            if self.request.user.is_superuser:
                return HttpResponseRedirect("/admin/")
            return HttpResponseRedirect("hilfe")
        elif usergroup == "Assistenten":
            return HttpResponseRedirect("schicht_tabelle")
        elif usergroup == "Assistenznehmer":
            return HttpResponseRedirect("hilfe")
        else:
            return HttpResponseRedirect("hilfe")
