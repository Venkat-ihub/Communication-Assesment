# survey/urls.py

from django.urls import path
from .views import survey_view, thank_you_view, test_view

urlpatterns = [
    path('', survey_view, name='survey'),
    path('thank-you/', thank_you_view, name='thank_you'),
    path('test/', test_view, name='test_view'),
]