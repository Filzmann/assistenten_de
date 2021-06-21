from django.urls import path
from .views.askhole import AskholeView
from .views.edit_asn_view import CreateAsnView, EditAsnView, DeleteFesteSchichtenView, DeleteSchichtTemplateView
from .views.edit_assistent_view import EditAssistentView
from .views.edit_au_view import CreateAUView, EditAUView, DeleteAUView
from .views.edit_schicht_view import CreateSchichtView, EditSchichtView, DeleteSchichtView
from .views.edit_urlaub_view import CreateUrlaubView, EditUrlaubView, DeleteUrlaubView
from .views.einkommenssteuer_view import EinkommenssteuerView
from .views.hilfe_view import HilfeView
from .views.schicht_tabelle_view import AsSchichtTabellenView

urlpatterns = [
    path('hife', HilfeView.as_view(), name='hilfe'),
    path('', AsSchichtTabellenView.as_view(), name='schicht_tabelle'),
    path('schicht_tabelle/<int:year>/<int:month>', AsSchichtTabellenView.as_view(), name='schicht_tabelle'),
    path('edit_as/<int:pk>', EditAssistentView.as_view(), name='edit_as'),
    path('create_asn', CreateAsnView.as_view(), name='create_asn'),
    path('edit_asn/<int:pk>', EditAsnView.as_view(), name='edit_asn'),
    path('del_feste_schicht/<int:pk>', DeleteFesteSchichtenView.as_view(), name='del_feste_schicht'),
    path('del_schicht_template/<int:pk>', DeleteSchichtTemplateView.as_view(), name='del_schicht_template'),
    path('create_schicht', CreateSchichtView.as_view(), name='create_schicht'),
    path('create_schicht/<str:y>/<str:m>/<str:d>', CreateSchichtView.as_view(), name='create_schicht'),
    path('edit_schicht/<int:pk>', EditSchichtView.as_view(), name='edit_schicht'),
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
