from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import ProgrammingError
from .forms import UserRegisterForm, RequestForm, UserProfileForm
from .models import User, Category, Product, Order, Payment, Review, SupportTicket, Record
from .serializers import (
    UserSerializer, CategorySerializer, ProductSerializer,
    OrderSerializer, PaymentSerializer, ReviewSerializer,
    SupportTicketSerializer, RecordSerializer
)
from rest_framework import viewsets, permissions

def home(request):
    try:
        reviews = Review.objects.all().order_by('-created_at')[:6]  # Get the 6 most recent reviews
    except Exception as e:
        # Si la table n'existe pas ou s'il y a une autre erreur, on passe une liste vide
        reviews = []
        print(f"Erreur lors de la récupération des reviews: {str(e)}")
    
    response = render(request, 'home/home.html', {'reviews': reviews})
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response

def signIN(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if not username or not password:
            messages.error(request, 'Veuillez remplir tous les champs.')
            return render(request, 'auth/login.html')
        
        try:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Connexion réussie !')
                return redirect('home')
            else:
                # Vérifier si l'utilisateur existe
                try:
                    User.objects.get(username=username)
                    messages.error(request, 'Mot de passe incorrect.')
                except User.DoesNotExist:
                    messages.error(request, 'Nom d\'utilisateur incorrect.')
        except Exception as e:
            messages.error(request, f'Une erreur est survenue : {str(e)}')
    
    # Si l'utilisateur est déjà connecté, rediriger vers la page d'accueil
    if request.user.is_authenticated:
        return redirect('home')
        
    return render(request, 'auth/login.html')

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            try:
                # Vérifier si le nom d'utilisateur existe déjà
                if User.objects.filter(username=form.cleaned_data['username']).exists():
                    messages.error(request, 'Ce nom d\'utilisateur est déjà pris.')
                    return render(request, 'auth/register.html', {'form': form})
                
                # Vérifier si l'email existe déjà
                if User.objects.filter(email=form.cleaned_data['email']).exists():
                    messages.error(request, 'Cet email est déjà utilisé.')
                    return render(request, 'auth/register.html', {'form': form})
                
                user = form.save(commit=False)
                user.set_password(form.cleaned_data['password1'])
                user.save()
                
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password1')
                
                # Authentifier l'utilisateur immédiatement après l'inscription
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    messages.success(request, 'Inscription réussie ! Bienvenue sur votre espace personnel.')
                    return redirect('account')
                else:
                    messages.error(request, 'Erreur lors de la connexion automatique. Veuillez vous connecter manuellement.')
                    return redirect('signIN')
            except Exception as e:
                messages.error(request, f'Une erreur est survenue lors de l\'inscription : {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Erreur dans le champ {field}: {error}")
    else:
        form = UserRegisterForm()
    return render(request, 'auth/register.html', {'form': form})

@login_required
def account(request):
    user = request.user
    orders = Order.objects.filter(user=user)
    payments = Payment.objects.filter(user=user).values('id', 'amount', 'status', 'created_at')
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Votre profil a été mis à jour avec succès !')
            return redirect('account')
    else:
        form = UserProfileForm(instance=user)
    
    return render(request, 'account/account.html', {
        'user': user,
        'orders': orders,
        'payments': payments,
        'form': form
    })

def netflix_page(request):
    return render(request, 'netflix_page.html')

def spotify_page(request):
    return render(request, 'spotify_page.html')

def about(request):
    return render(request, 'about.html')

def offer(request):
    products = Product.objects.filter(status='available')
    return render(request, 'home/home.html', {'products': products})

def submit_request(request):
    if request.method == 'POST':
        form = RequestForm(request.POST)
        if form.is_valid():
            # Créer un nouvel enregistrement
            record = Record.objects.create(
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone'],
                address=form.cleaned_data['address'],
                city=form.cleaned_data['city']
            )
            messages.success(request, 'Votre demande a été enregistrée avec succès !')
            return redirect('home')
        else:
            messages.error(request, 'Veuillez corriger les erreurs dans le formulaire.')
    else:
        form = RequestForm()
    return render(request, 'home/home.html', {'form': form})

def test_images(request):
    return render(request, 'test_images.html')

def disney_page(request):
    return render(request, 'disney_page.html')

def crunchyroll_page(request):
    return render(request, 'crunchyroll_page.html')

def payment_success(request):
    order_id = request.GET.get('order_id', '')
    return render(request, 'payment/success.html', {'order_id': order_id})

def payment_fail(request):
    error = request.GET.get('error', 'Une erreur est survenue lors du traitement de votre paiement.')
    return render(request, 'payment/fail.html', {'error': error})

def terms_of_use(request):
    return render(request, 'footer/terms_of_use.html')

def privacy_policy(request):
    return render(request, 'footer/privacy_policy.html')

def faq(request):
    return render(request, 'footer/faq.html')

def contact(request):
    return render(request, 'contact.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'Vous avez été déconnecté avec succès.')
    return redirect('home')

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=self.request.user)

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Payment.objects.all()
        return Payment.objects.filter(user=self.request.user)

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Review.objects.all()
        return Review.objects.filter(user=self.request.user)

class SupportTicketViewSet(viewsets.ModelViewSet):
    queryset = SupportTicket.objects.all()
    serializer_class = SupportTicketSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return SupportTicket.objects.all()
        return SupportTicket.objects.filter(user=self.request.user)

class RecordViewSet(viewsets.ModelViewSet):
    queryset = Record.objects.all()
    serializer_class = RecordSerializer
    permission_classes = [permissions.IsAuthenticated]

# Reviews (Avis)
def review_list(request):
    reviews = Review.objects.all().order_by('-created_at')
    return render(request, 'reviews/review_list.html', {'reviews': reviews})

@login_required
def add_review(request):
    if request.method == 'POST':
        service = request.POST.get('service')
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        
        if not all([service, rating, comment]):
            messages.error(request, 'Veuillez remplir tous les champs.')
            return render(request, 'reviews/add_review.html')
        
        try:
            rating = int(rating)
            if not (1 <= rating <= 5):
                raise ValueError('Invalid rating')
                
            Review.objects.create(
                user=request.user,
                service=service,
                rating=rating,
                comment=comment
            )
            messages.success(request, 'Votre avis a été publié avec succès !')
            return redirect('review_list')
        except (ValueError, TypeError):
            messages.error(request, 'Une erreur est survenue. Veuillez réessayer.')
            
    return render(request, 'reviews/add_review.html')

# Products
def product_list(request):
    products = Product.objects.filter(status='available').order_by('-created_at')
    categories = Category.objects.all()
    return render(request, 'products/product_list.html', {
        'products': products,
        'categories': categories
    })

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = product.reviews.all().order_by('-created_at')
    return render(request, 'products/product_detail.html', {
        'product': product,
        'reviews': reviews
    })

# Support Tickets
def support_ticket_list(request):
    if not request.user.is_authenticated:
        return redirect('login')
    tickets = SupportTicket.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'support/ticket_list.html', {'tickets': tickets})

def create_support_ticket(request):
    if not request.user.is_authenticated:
        return redirect('login')
        
    if request.method == 'POST':
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        SupportTicket.objects.create(
            user=request.user,
            subject=subject,
            message=message
        )
        return redirect('support_ticket_list')
        
    return render(request, 'support/create_ticket.html')

def ticket_detail(request, ticket_id):
    if not request.user.is_authenticated:
        return redirect('login')
    ticket = get_object_or_404(SupportTicket, id=ticket_id, user=request.user)
    return render(request, 'support/ticket_detail.html', {'ticket': ticket})

# Streaming Video Services
def hbomax_page(request):
    return render(request, 'services/hbomax_page.html')

def prime_page(request):
    return render(request, 'services/prime_page.html')

def hulu_page(request):
    return render(request, 'services/hulu_page.html')

def appletv_page(request):
    return render(request, 'services/appletv_page.html')

def paramount_page(request):
    return render(request, 'services/paramount_page.html')

def peacock_page(request):
    return render(request, 'services/peacock_page.html')

# Music Services
def applemusic_page(request):
    return render(request, 'services/applemusic_page.html')

def youtubemusic_page(request):
    return render(request, 'services/youtubemusic_page.html')

def deezer_page(request):
    return render(request, 'services/deezer_page.html')

# Gaming Services
def xbox_page(request):
    return render(request, 'services/xbox_page.html')

def playstation_page(request):
    return render(request, 'services/playstation_page.html')

def eaplay_page(request):
    return render(request, 'services/eaplay_page.html')

def ubisoft_page(request):
    return render(request, 'services/ubisoft_page.html')
