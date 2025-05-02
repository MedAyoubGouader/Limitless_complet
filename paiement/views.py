from django.shortcuts import render, redirect
from .models import Transaction
from datetime import datetime
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from website.models import Payment, Order, User, Product
import stripe
import json

#render : permet de retourner un template HTML.

#redirect : redirige l'utilisateur vers une autre page (ex : succès ou échec).

#transaction : modèle utilisé pour enregistrer les paiements dans la base.

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

# 💳 Page de formulaire de paiement et traitement
@require_POST
def payer(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'Vous devez être connecté pour effectuer un paiement.'})

    try:
        # Récupérer les données du formulaire
        product_name = request.POST.get('product')
        plan = request.POST.get('plan')
        price_str = request.POST.get('price', '0')
        
        # Validation des données requises
        if not all([product_name, plan, price_str]):
            return JsonResponse({
                'success': False,
                'message': 'Données manquantes'
            })
        
        # Validation et conversion du prix
        try:
            # Remplacer la virgule par un point pour la conversion
            price_str = price_str.replace(',', '.')
            price = float(price_str)
            if price <= 0:
                raise ValueError("Le montant doit être supérieur à 0")
        except ValueError as e:
            return JsonResponse({
                'success': False,
                'message': f'Montant invalide: {str(e)}'
            })
        
        # Récupérer l'objet Product en gérant les variantes de noms
        try:
            # Essayer d'abord avec le nom exact
            product_obj = Product.objects.get(name=product_name)
        except Product.DoesNotExist:
            try:
                # Si non trouvé, essayer avec le nom de base (sans "Premium", "Plus", etc.)
                base_name = product_name.split()[0]  # Prendre le premier mot
                product_obj = Product.objects.get(name=base_name)
            except Product.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': f'Produit "{product_name}" non trouvé'
                })
        
        # Créer une commande
        order = Order.objects.create(
            user=request.user,
            product=product_obj,
            price=price,
            status='pending'
        )

        # Créer l'intention de paiement Stripe
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(price * 100),  # Stripe utilise les centimes
                currency='tnd',
                metadata={
                    'order_id': str(order.id),
                    'product': product_name,
                    'plan': plan
                }
            )
        except stripe.error.StripeError as e:
            # En cas d'erreur Stripe, annuler la commande
            order.status = 'cancelled'
            order.save()
            return JsonResponse({
                'success': False,
                'message': f'Erreur de paiement: {str(e)}'
            })

        # Créer l'enregistrement de paiement
        payment = Payment.objects.create(
            user=request.user,
            amount=price,
            status='pending'
        )

        return JsonResponse({
            'success': True,
            'client_secret': intent.client_secret,
            'order_id': str(order.id)
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Une erreur est survenue: {str(e)}'
        })

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return JsonResponse({'error': 'Invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError as e:
        return JsonResponse({'error': 'Invalid signature'}, status=400)

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
            
            # Envoyer un email de confirmation ici
            
        except (Order.DoesNotExist, Payment.DoesNotExist):
            return JsonResponse({'error': 'Order not found'}, status=404)

    return JsonResponse({'status': 'success'})

# ✅ Routes de simulation simple (optionnelles)
def simulate_payment_success(request):
    return HttpResponse("✅ Paiement simulé réussi.")

def simulate_payment_fail(request):
    return HttpResponse("❌ Paiement simulé échoué.")

# ✅ Pages de résultat
def success(request):
    order_id = request.GET.get('order_id')
    return render(request, 'payment/success.html', {'order_id': order_id})

def fail(request):
    error = request.GET.get('error', 'Une erreur est survenue lors du paiement.')
    return render(request, 'payment/fail.html', {'error': error})
