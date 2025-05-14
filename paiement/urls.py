from django.urls import path
from . import views
#Elle importe les outils Django pour définir des URLs (path).  Elle importe toutes les fonctions (vues) depuis ton fichier views.py.
urlpatterns = [
    path('payer/', views.payer, name='payer'),
    path('payment-form/', views.payment_form, name='payment_form'),
    path('success/', views.success, name='success'),
    path('fail/', views.fail, name='fail'),
]
