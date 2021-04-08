from django.urls import path
from . import views
from .views.edit_asn_view import CreateAsnView, EditAsnView
from .views.edit_assistent_view import EditAssistentView

urlpatterns = [
    path('', views.index, name='index'),
    path('edit_as/<int:pk>', EditAssistentView.as_view(), name='edit_as'),
    path('create_asn', CreateAsnView.as_view(), name='create_asn'),
    path('edit_asn/<int:pk>', EditAsnView.as_view(), name='edit_asn'),
]
