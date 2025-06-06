# Generated by Django 5.1.6 on 2025-04-12 06:03

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom_client', models.CharField(max_length=100)),
                ('email_client', models.EmailField(max_length=254)),
                ('montant', models.DecimalField(decimal_places=2, max_digits=8)),
                ('numero_carte', models.CharField(max_length=16)),
                ('statut', models.CharField(choices=[('succès', 'Succès'), ('échec', 'Échec')], max_length=10)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
    ]
