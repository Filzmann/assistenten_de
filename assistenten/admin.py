from django.contrib import admin

# Register your models here.
from .models import Assistent
from .models import ASN
from .models import EB
from .models import PFK
from .models import Lohn
from .models import Adresse

admin.site.register(Assistent)
admin.site.register(ASN)
admin.site.register(EB)
admin.site.register(PFK)
admin.site.register(Lohn)
admin.site.register(Adresse)