# Generated by Django 5.0.6 on 2024-07-21 13:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appsimulation', '0002_alter_simulation_date_creation'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=150, unique=True)),
                ('password1', models.CharField(max_length=128)),
            ],
        ),
        migrations.DeleteModel(
            name='Utilisateur',
        ),
    ]