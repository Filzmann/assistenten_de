from django.contrib import admin

# Register your models here.
from guardian.admin import GuardedModelAdmin

from .models import Assistent, Schicht, Weg
from .models import ASN
from .models import EB
from .models import PFK
from .models import Lohn
from .models import Adresse


class AssistentAdmin(GuardedModelAdmin):
    prepopulated_fields = {"email": ('name', 'vorname', 'email')}
    list_display = ('email', 'name', 'vorname')
    search_fields = ('name', 'vorname', 'email')
    ordering = ('-name',)
    # date_hierarchy = 'created_at'


admin.site.register(Assistent, AssistentAdmin)
admin.site.register(ASN)
admin.site.register(EB)
admin.site.register(PFK)
admin.site.register(Lohn)
admin.site.register(Adresse)
admin.site.register(Schicht)
admin.site.register(Weg)
