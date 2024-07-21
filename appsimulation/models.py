from django.db import models
from django.utils import timezone 
class User(models.Model):
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)  # Pour des raisons de sécurité, n'utilisez pas cela en production

    def __str__(self):
        return self.username


class Client(models.Model):
    idclient = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=255)
    prenom = models.CharField(max_length=255)
    telephone = models.IntegerField()

    def __str__(self):
        return f"{self.nom} {self.prenom}"

class Service(models.Model):
    idservice = models.AutoField(primary_key=True)
    libelle = models.CharField(max_length=255)
    prix = models.IntegerField()

    def __str__(self):
        return f"{self.libelle} {self.prix} FCFA"



class Simulation(models.Model):
    id_simulation = models.AutoField(primary_key=True)
    titre = models.CharField(max_length=255)
    designation = models.CharField(max_length=255)
    prix = models.DecimalField(max_digits=12, decimal_places=2)
    quantite = models.IntegerField()
    prix_total_achat = models.DecimalField(max_digits=12, decimal_places=2)
    montant_transit = models.DecimalField(max_digits=12, decimal_places=2)
    montant_douane = models.DecimalField(max_digits=12, decimal_places=2)
    pourcentage_banque = models.DecimalField(max_digits=12, decimal_places=2)
    pourcentage_banque_montant = models.DecimalField(max_digits=12, decimal_places=2)
    prix_de_revient_total = models.DecimalField(max_digits=12, decimal_places=2)
    marge_pourcentage = models.DecimalField(max_digits=12, decimal_places=2)
    marge_montant = models.DecimalField(max_digits=12, decimal_places=2)
    isb =models.DecimalField(max_digits=12, decimal_places=2)
    prix_vente_total_ht_sans_isb = models.DecimalField(max_digits=12, decimal_places=2)
    prix_vente_total_ht_avec_isb = models.DecimalField(max_digits=12, decimal_places=2)
    prix_vente_total_ht = models.DecimalField(max_digits=12, decimal_places=2)
    
    total_ht_devis = models.DecimalField(max_digits=12, decimal_places=2)
    total_ttc_devis = models.DecimalField(max_digits=12, decimal_places=2)
    marge_montant_total = models.DecimalField(max_digits=12, decimal_places=2)
    total_prix_revient = models.DecimalField(max_digits=12, decimal_places=2)
    total_isb = models.DecimalField(max_digits=12, decimal_places=2)
    total_tva = models.DecimalField(max_digits=12, decimal_places=2)
    date_creation = models.DateTimeField(default=timezone.now)


