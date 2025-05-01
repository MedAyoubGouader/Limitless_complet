from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
import uuid

# Modèle pour les enregistrements généraux (déjà utilisé dans ton admin)
class Record(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    phone = models.CharField(max_length=15)
    address = models.TextField(max_length=100)
    city = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

# ✅ Nouveau modèle pour les clients Limitless
# Etape 1 : Corriger models.py (dans website/models.py)
# website/models.py

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    role = models.CharField(
        max_length=10,
        choices=[
            ('buyer', 'Acheteur'),
            ('seller', 'Vendeur'),
            ('admin', 'Administrateur')
        ],
        default='buyer'
    )
    profile_photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = _('Utilisateur')
        verbose_name_plural = _('Utilisateurs')

    def __str__(self):
        return self.username

    def get_purchase_history(self):
        """
        Retourne l'historique d'achat de l'utilisateur
        """
        return {
            'orders': self.orders.all().order_by('-created_at'),
            'payments': self.payments.all().order_by('-created_at'),
            'total_spent': sum(order.price for order in self.orders.filter(status='completed')),
            'total_orders': self.orders.count(),
            'completed_orders': self.orders.filter(status='completed').count(),
            'pending_orders': self.orders.filter(status='pending').count(),
            'cancelled_orders': self.orders.filter(status='cancelled').count()
        }

class Category(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, help_text="Font Awesome icon class", default="fas fa-folder")
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    features = models.TextField(help_text="List of features, one per line", blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['category', 'order', 'name']
    
    def __str__(self):
        return self.name

class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='orders')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=10,
        choices=[
            ('pending', 'En attente'),
            ('completed', 'Terminée'),
            ('cancelled', 'Annulée')
        ],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Commande')
        verbose_name_plural = _('Commandes')

    def __str__(self):
        return f"Commande {self.id} - {self.product.name}"

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Payment {self.id} - {self.user.username}"

class Review(models.Model):
    SERVICE_CHOICES = [
        ('netflix', 'Netflix'),
        ('disney', 'Disney+'),
        ('hbo', 'HBO Max'),
        ('prime', 'Amazon Prime Video'),
        ('hulu', 'Hulu'),
        ('apple_tv', 'Apple TV+'),
        ('paramount', 'Paramount+'),
        ('peacock', 'Peacock'),
        ('spotify', 'Spotify Premium'),
        ('apple_music', 'Apple Music'),
        ('youtube_music', 'YouTube Music Premium'),
        ('tidal', 'Tidal'),
        ('deezer', 'Deezer'),
        ('audible', 'Audible'),
        ('kindle', 'Kindle Unlimited'),
        ('scribd', 'Scribd'),
        ('storytel', 'Storytel'),
        ('xbox', 'Xbox Game Pass'),
        ('playstation', 'PlayStation Plus'),
        ('nintendo', 'Nintendo Switch Online'),
        ('ea_play', 'EA Play'),
        ('ubisoft', 'Ubisoft+'),
        ('geforce', 'GeForce NOW'),
        ('crunchyroll', 'Crunchyroll Premium'),
        ('google_one', 'Google One'),
        ('microsoft_365', 'Microsoft 365'),
        ('dropbox', 'Dropbox Plus/Professional'),
        ('icloud', 'iCloud+'),
        ('adobe', 'Adobe Creative Cloud'),
        ('chatgpt', 'ChatGPT Plus'),
        ('grammarly', 'Grammarly Premium'),
        ('canva', 'Canva Pro'),
        ('notion', 'Notion Plus'),
        ('figma', 'Figma Professional'),
        ('zoom', 'Zoom Pro'),
        ('nyt', 'The New York Times'),
        ('wapo', 'The Washington Post'),
        ('economist', 'The Economist'),
        ('wsj', 'The Wall Street Journal'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    service = models.CharField(max_length=50, choices=SERVICE_CHOICES,blank=True, null=True)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)],blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'website_review'  # Explicitly set the table name
        unique_together = ('user', 'service')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}'s review of {self.service}"

class SupportTicket(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='support_tickets')
    subject = models.CharField(max_length=255)
    message = models.TextField()
    status = models.CharField(
        max_length=10,
        choices=[
            ('open', 'Ouvert'),
            ('resolved', 'Résolu'),
            ('closed', 'Fermé')
        ],
        default='open'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Ticket de support')
        verbose_name_plural = _('Tickets de support')

    def __str__(self):
        return f"Ticket {self.id} - {self.subject}"
