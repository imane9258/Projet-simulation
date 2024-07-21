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


from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm as DjangoUserCreationForm

class UserCreationForm(DjangoUserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Un utilisateur avec ce nom existe déjà.")
        return username
    

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        if len(password2) < 8:
            raise forms.ValidationError("Le mot de passe doit contenir au moins 8 caractères.")
        if password2.lower() in self.cleaned_data.get('username', '').lower():
            raise forms.ValidationError("Le mot de passe est trop semblable au nom d’utilisateur.")
        return password2

from django import forms
from django.contrib.auth.forms import UserChangeForm as DjangoUserChangeForm
from django.contrib.auth.models import User

class UserUpdateForm(DjangoUserChangeForm):
    password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(),
        required=False,
        help_text='Leave blank if you do not want to change the password'
    )
    password2 = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(),
        required=False
    )

    class Meta:
        model = User
        fields = ['username']  # Inclure uniquement les champs que vous souhaitez afficher/modifier

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        
        if password1 and password1 != password2:
            self.add_error('password2', "The two password fields must match.")
        
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password1')
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user
