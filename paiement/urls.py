from django.urls import path
from . import views
#Elle importe les outils Django pour définir des URLs (path).  Elle importe toutes les fonctions (vues) depuis ton fichier views.py.
urlpatterns = [
    path('payer/', views.payer, name='payer'),
    path('simulate/success/', views.simulate_payment_success, name='simulate_success'),
    path('simulate/fail/', views.simulate_payment_fail, name='simulate_fail'),
    path('success/', views.success, name='success'),
    path('fail/', views.fail, name='fail'),
    path('webhook/', views.stripe_webhook, name='stripe_webhook'),
]
