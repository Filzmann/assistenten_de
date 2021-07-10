from django.urls import path
from .views.askhole import AskholeView
from .views.as_edit_asn_view import AsCreateAsnView, AsEditAsnView, DeleteFesteSchichtenView, DeleteSchichtTemplateView
from .views.as_edit_assistent_view import AsEditAssistentView
from .views.asn_dienstplan import AsnDienstplanView
from .views.asn_edit_as_view import AsnCreateAsView, AsnEditAsView
from .views.asn_edit_asn_view import AsnEditAsnView
from .views.asn_edit_schicht_view import AsnCreateSchichtView, AsnEditSchichtView
from .views.edit_au_view import CreateAUView, EditAUView, DeleteAUView
from .views.as_edit_schicht_view import AsCreateSchichtView, AsEditSchichtView, DeleteSchichtView
from .views.edit_urlaub_view import CreateUrlaubView, EditUrlaubView, DeleteUrlaubView
from .views.einkommenssteuer_view import EinkommenssteuerView
from .views.group_based_redirector import GroupBasedRedirector
from .views.hilfe_view import HilfeView
from .views.as_schicht_tabelle_view import AsSchichtTabellenView

urlpatterns = [
    path('hilfe', HilfeView.as_view(), name='hilfe'),
    path('', GroupBasedRedirector.as_view(), name='index'),

    # Assistenten
    path('as_schicht_tabelle', AsSchichtTabellenView.as_view(), name='as_schicht_tabelle'),
    path('as_schicht_tabelle/<int:year>/<int:month>', AsSchichtTabellenView.as_view(), name='as_schicht_tabelle'),
    path('as_edit_as/<int:pk>', AsEditAssistentView.as_view(), name='as_edit_as'),
    path('as_create_asn', AsCreateAsnView.as_view(), name='as_create_asn'),
    path('as_edit_asn/<int:pk>', AsEditAsnView.as_view(), name='as_edit_asn'),
    path('as_create_schicht', AsCreateSchichtView.as_view(), name='as_create_schicht'),
    path('as_create_schicht/<str:y>/<str:m>/<str:d>', AsCreateSchichtView.as_view(), name='as_create_schicht'),
    path('as_edit_schicht/<int:pk>', AsEditSchichtView.as_view(), name='as_edit_schicht'),
    # ASN

    path('asn_dienstplan', AsnDienstplanView.as_view(), name='asn_dienstplan'),
    path('asn_dienstplan/<int:year>/<int:month>', AsnDienstplanView.as_view(), name='asn_dienstplan'),
    path('asn_edit_asn/<int:pk>', AsnEditAsnView.as_view(), name='asn_edit_asn'),
    path('asn_create_as', AsnCreateAsView.as_view(), name='asn_create_as'),
    path('asn_edit_as/<int:pk>', AsnEditAsView.as_view(), name='asn_edit_as'),
    path('asn_create_schicht', AsnCreateSchichtView.as_view(), name='asn_create_schicht'),
    path('asn_create_schicht/<str:y>/<str:m>/<str:d>', AsnCreateSchichtView.as_view(), name='asn_create_schicht'),
    path('asn_edit_schicht/<int:pk>', AsnEditSchichtView.as_view(), name='asn_edit_schicht'),

    path('del_feste_schicht/<int:pk>', DeleteFesteSchichtenView.as_view(), name='del_feste_schicht'),
    path('del_schicht_template/<int:pk>', DeleteSchichtTemplateView.as_view(), name='del_schicht_template'),

    path('del_schicht/<int:pk>', DeleteSchichtView.as_view(), name='del_schicht'),
    path('create_urlaub', CreateUrlaubView.as_view(), name='create_urlaub'),
    path('edit_urlaub/<int:pk>', EditUrlaubView.as_view(), name='edit_urlaub'),
    path('del_urlaub/<int:pk>', DeleteUrlaubView.as_view(), name='del_urlaub'),
    path('create_au', CreateAUView.as_view(), name='create_au'),
    path('edit_au/<int:pk>', EditAUView.as_view(), name='edit_au'),
    path('del_au/<int:pk>', DeleteAUView.as_view(), name='del_au'),
    path('einkommenssteuer', EinkommenssteuerView.as_view(), name='einkommenssteuer'),
    path('askhole', AskholeView.as_view(), name='askhole'),

]
