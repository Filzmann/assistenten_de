from datetime import timedelta
from django.db.models import Q
from assistenten.models import Schicht, Brutto, AU, Urlaub



def sort_schicht_data_by_beginn(schichten: list):
    """sortiert die schichten an einem tag (in Form einer Liste von dicts von strings)
    nach ihrem beginn"""
    return sorted(schichten, key=lambda j: j['von'])
