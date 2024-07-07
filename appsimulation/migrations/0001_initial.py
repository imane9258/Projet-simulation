# Generated by Django 5.0.6 on 2024-07-07 13:53

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('idclient', models.AutoField(primary_key=True, serialize=False)),
                ('nom', models.CharField(max_length=255)),
                ('prenom', models.CharField(max_length=255)),
                ('telephone', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('idservice', models.AutoField(primary_key=True, serialize=False)),
                ('libelle', models.CharField(max_length=255)),
                ('prix', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Simulation',
            fields=[
                ('id_simulation', models.AutoField(primary_key=True, serialize=False)),
                ('titre', models.CharField(max_length=255)),
                ('designation', models.CharField(max_length=255)),
                ('prix', models.DecimalField(decimal_places=2, max_digits=12)),
                ('quantite', models.IntegerField()),
                ('prix_total_achat', models.DecimalField(decimal_places=2, max_digits=12)),
                ('montant_transit', models.DecimalField(decimal_places=2, max_digits=12)),
                ('montant_douane', models.DecimalField(decimal_places=2, max_digits=12)),
                ('pourcentage_banque', models.DecimalField(decimal_places=2, max_digits=12)),
                ('pourcentage_banque_montant', models.DecimalField(decimal_places=2, max_digits=12)),
                ('prix_de_revient_total', models.DecimalField(decimal_places=2, max_digits=12)),
                ('marge_pourcentage', models.DecimalField(decimal_places=2, max_digits=12)),
                ('marge_montant', models.DecimalField(decimal_places=2, max_digits=12)),
                ('isb', models.DecimalField(decimal_places=2, max_digits=12)),
                ('prix_vente_total_ht_sans_isb', models.DecimalField(decimal_places=2, max_digits=12)),
                ('prix_vente_total_ht_avec_isb', models.DecimalField(decimal_places=2, max_digits=12)),
                ('prix_vente_total_ht', models.DecimalField(decimal_places=2, max_digits=12)),
                ('total_ht_devis', models.DecimalField(decimal_places=2, max_digits=12)),
                ('total_ttc_devis', models.DecimalField(decimal_places=2, max_digits=12)),
                ('marge_montant_total', models.DecimalField(decimal_places=2, max_digits=12)),
                ('total_prix_revient', models.DecimalField(decimal_places=2, max_digits=12)),
                ('total_isb', models.DecimalField(decimal_places=2, max_digits=12)),
                ('total_tva', models.DecimalField(decimal_places=2, max_digits=12)),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Utilisateur',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=50)),
                ('mot_de_passe', models.CharField(max_length=50)),
            ],
        ),
    ]
