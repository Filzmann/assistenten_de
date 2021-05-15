from django.urls import path
from . import views
from .views.edit_asn_view import CreateAsnView, EditAsnView, DeleteFesteSchichtenView, DeleteSchichtTemplateView
from .views.edit_assistent_view import EditAssistentView
from .views.edit_schicht_view import CreateSchichtView, EditSchichtView, DeleteSchichtView
from .views.schicht_tabelle_view import AsSchichtTabellenView

urlpatterns = [
    # path('', views.index, name='index'),
    path('', AsSchichtTabellenView.as_view(), name='schicht_tabelle'),
    path('schicht_tabelle/<int:year>/<int:month>', AsSchichtTabellenView.as_view(), name='schicht_tabelle'),
    path('edit_as/<int:pk>', EditAssistentView.as_view(), name='edit_as'),
    path('create_asn', CreateAsnView.as_view(), name='create_asn'),
    path('edit_asn/<int:pk>', EditAsnView.as_view(), name='edit_asn'),
    path('del_feste_schicht/<int:pk>', DeleteFesteSchichtenView.as_view(), name='del_feste_schicht'),
    path('del_schicht_template/<int:pk>', DeleteSchichtTemplateView.as_view(), name='del_schicht_template'),
    path('create_schicht', CreateSchichtView.as_view(), name='create_schicht'),
    path('create_schicht/<int:y>/<int:m>/<int:d>', CreateSchichtView.as_view(), name='create_schicht'),
    path('edit_schicht/<int:pk>', EditSchichtView.as_view(), name='edit_schicht'),
    path('del_schicht/<int:pk>', DeleteSchichtView.as_view(), name='del_schicht'),

]
