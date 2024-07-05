# forms.py
from django import forms
from .models import Simulation

class SimulationForm(forms.ModelForm):
    class Meta:
        model = Simulation
        fields = ['titre', 'designation', 'quantite', 'prix', 'montant_transit', 'montant_douane', 'pourcentage_banque', 'marge_pourcentage']
