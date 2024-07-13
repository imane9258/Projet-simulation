# forms.py
from django import forms
from .models import Simulation

class SimulationForm(forms.ModelForm):
    class Meta:
        model = Simulation
        fields = ['titre', 'designation', 'quantite', 'prix', 'montant_transit', 'montant_douane', 'pourcentage_banque', 'marge_pourcentage']


# Dans votre fichier forms.py
from django import forms

class FiltreSimulationForm(forms.Form):
    date_debut = forms.DateField(label='Date de début', widget=forms.DateInput(attrs={'type': 'date'}))
