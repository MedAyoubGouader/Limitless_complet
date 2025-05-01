from django.db import models
from django.utils import timezone

class Transaction(models.Model): #utilisé pour enregistrer chaque paiement dans ta base de données.
    nom_client = models.CharField(max_length=100)
    email_client = models.EmailField()
    montant = models.DecimalField(max_digits=8, decimal_places=2)
    numero_carte = models.CharField(max_length=16)  # champ fictif
    statut = models.CharField(max_length=10, choices=[('succès', 'Succès'), ('échec', 'Échec')])
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.nom_client} - {self.montant} DT - {self.statut}"
