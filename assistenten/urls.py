from django.urls import path
from . import views
from .views.edit_assistent_view import EditAssistentView

urlpatterns = [
    path('', views.index, name='index'),
    path('edit_as/<int:pk>', EditAssistentView.as_view(), name='edit_as'),
]
