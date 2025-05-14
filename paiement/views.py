from django.shortcuts import render, redirect
from datetime import datetime
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from website.models import Payment, Order, User, Product
import stripe
import json
from django.contrib.auth.decorators import login_required
import time
import traceback
import uuid

#render : permet de retourner un template HTML.

#redirect : redirige l'utilisateur vers une autre page (ex : succès ou échec).

#datetime : utilisé pour vérifier si la date d'expiration est dans le futur.

#HttpResponse : retourne un message HTML simple (utile pour debug ou confirmation).

# Liste des cartes valides fictives
CARTES_VALIDES = [
    {"numero": "4111111111111111", "nom": "Ayoub Gouader", "cvc": "123", "expiration": "2025-08"},
    {"numero": "5555555555554444", "nom": "Nour Ben Amor", "cvc": "321", "expiration": "2026-04"},
    {"numero": "4000123412341234", "nom": "Ahmed Mabrouk", "cvc": "111", "expiration": "2025-12"},
    {"numero": "5105105105105100", "nom": "Yasmine Souissi", "cvc": "222", "expiration": "2027-02"},
    {"numero": "4222222222222",     "nom": "Sami Jridi",     "cvc": "333", "expiration": "2025-10"},
    {"numero": "4012888888881881", "nom": "Sara Bouazizi",  "cvc": "999", "expiration": "2026-06"},
]

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

def validate_card(card_number, card_name, cvc, expiration):
    """Valide une carte de crédit fictive"""
    print(f"Validation de la carte:")
    print(f"Numéro: {card_number}")
    print(f"Nom: {card_name}")
    print(f"CVC: {cvc}")
    print(f"Expiration: {expiration}")
    
    for card in CARTES_VALIDES:
        print(f"Comparaison avec la carte: {card}")
        if (card['numero'] == card_number and 
            card['nom'] == card_name and 
            card['cvc'] == cvc and 
            card['expiration'] == expiration):
            print("Carte valide trouvée!")
            return True
    print("Aucune carte valide trouvée")
    return False

@login_required
def payment_form(request):
    """Vue pour charger le formulaire de paiement"""
    product = request.GET.get('product', '')
    plan = request.GET.get('plan', '')
    price = request.GET.get('price', '')
    return render(request, 'paiement/payment_form.html', {
        'product': product,
        'plan': plan,
        'price': price,
    })

@login_required
@csrf_exempt
def payer(request):
    if request.method == 'POST':
        try:
            print("Début du traitement du paiement (mode démo)")
            data = json.loads(request.body)
            print(f"Données reçues: {data}")
            expiration = f"{data['exp_year']}-{data['exp_month'].zfill(2)}"
            print(f"Date d'expiration formatée: {expiration}")
            print("Validation de la carte...")
            if not validate_card(
                data['card_number'], 
                data['card_name'], 
                data['cvc'], 
                expiration
            ):
                print("Carte invalide")
                return JsonResponse({'success': False, 'error': 'Carte de crédit invalide'}, status=400)
            print("Carte valide (mode démo)")
            
            # Récupérer les informations du produit, du plan et du prix depuis la requête
            product_name = request.GET.get('product', '')
            plan = request.GET.get('plan', '')
            price = request.GET.get('price', '')
            
            # Récupérer l'utilisateur connecté
            user = request.user
            
            # Créer une commande
            try:
                product = Product.objects.get(name=product_name)
            except Product.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Produit non trouvé'}, status=400)
            
            order = Order.objects.create(
                user=user,
                product=product,
                plan=plan,
                price=price,
                status='completed'  # Simuler le paiement réussi
            )
            
            # Créer un paiement
            payment = Payment.objects.create(
                user=user,
                order=order,
                amount=price
            )
            
            print(f"Paiement simulé réussi, order_id: {order.id}")
            return JsonResponse({
                'success': True,
                'message': 'Paiement effectué avec succès (mode démo)',
                'order_id': str(order.id)
            })
        except Exception as e:
            print(f"Erreur détaillée lors du paiement: {str(e)}")
            print(f"Traceback complet: {traceback.format_exc()}")
            return JsonResponse({
                'success': False, 
                'error': f'Erreur serveur: {str(e)}'
            }, status=500)
    return JsonResponse({
        'success': False, 
        'error': 'Méthode non autorisée'
    }, status=405)

@login_required
def success(request):
    order_id = request.GET.get('order_id')
    try:
        order = Order.objects.get(id=order_id)
        product = order.product
        payment = Payment.objects.get(order=order)
        message = "Merci pour votre achat ! (mode démo) Les identifiants du compte vous seront envoyés par email dans quelques minutes."
        return render(request, 'paiement/success.html', {
            'order': order,
            'product': product,
            'payment': payment,
            'message': message
        })
    except Order.DoesNotExist:
        return render(request, 'paiement/success.html', {
            'order': None,
            'product': None,
            'payment': None,
            'message': "Merci pour votre achat ! (mode démo) Les identifiants du compte vous seront envoyés par email dans quelques minutes. (Order not found)"
        })

@login_required
def fail(request):
    error = request.GET.get('error', 'Une erreur est survenue lors du paiement')
    return render(request, 'paiement/fail.html', {'error': error})

@csrf_exempt
def stripe_webhook(request):
    if request.method == 'POST':
        try:
            event = json.loads(request.body)
            
            if event['type'] == 'payment_intent.succeeded':
                payment_intent = event['data']['object']
                order_id = payment_intent['metadata']['order_id']
                
                try:
                    order = Order.objects.get(id=order_id)
                    order.status = 'completed'
                    order.save()
                    
                    payment = Payment.objects.get(order=order)
                    payment.status = 'successful'
                    payment.save()
                    
                except (Order.DoesNotExist, Payment.DoesNotExist):
                    pass
                    
            elif event['type'] == 'payment_intent.payment_failed':
                payment_intent = event['data']['object']
                order_id = payment_intent['metadata']['order_id']
                
                try:
                    order = Order.objects.get(id=order_id)
                    order.status = 'failed'
                    order.save()
                    
                    payment = Payment.objects.get(order=order)
                    payment.status = 'failed'
                    payment.save()
                    
                except (Order.DoesNotExist, Payment.DoesNotExist):
                    pass
            
            return JsonResponse({'status': 'success'})
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

# ✅ Routes de simulation simple (optionnelles)
def simulate_payment_success(request):
    return HttpResponse("✅ Paiement simulé réussi.")

def simulate_payment_fail(request):
    return HttpResponse("❌ Paiement simulé échoué.")
