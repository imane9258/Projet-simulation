from django.urls import path
from . import api_views

urlpatterns = [
    path('connexion/', api_views.connexion, name='api_connexion'),
    path('simulations/', api_views.get_simulations, name='api_simulations'),
]
