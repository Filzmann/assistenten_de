from django.urls import reverse_lazy


def get_default_success_url_by_usergroup(user):
    usergroup = user.groups.values_list('name', flat=True).first()
    if usergroup == "Assistenten":
        return reverse_lazy("as_schicht_tabelle")
    elif usergroup == "Assistenznehmer":
        return reverse_lazy("asn_dienstplan")