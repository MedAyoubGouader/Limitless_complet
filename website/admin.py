from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import (
    User, Category, Product, Order, 
    Payment, Review, SupportTicket, Record
)

# Configuration personnalisée pour le modèle User
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'balance')
    list_filter = ('role',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone', 'address', 'city')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Additional info', {'fields': ('role', 'balance', 'profile_photo')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'email', 'role'),
        }),
    )

    def purchase_history(self, obj):
        history = obj.get_purchase_history()
        return format_html(
            '<a href="/admin/website/order/?user__id__exact={}">'
            'Commandes: {} ({} complétées, {} en attente, {} annulées)'
            '</a><br>'
            '<a href="/admin/website/payment/?user__id__exact={}">'
            'Paiements: {}'
            '</a><br>'
            'Total dépensé: {} TND',
            obj.id,
            history['total_orders'],
            history['completed_orders'],
            history['pending_orders'],
            history['cancelled_orders'],
            obj.id,
            history['payments'].count(),
            history['total_spent']
        )
    purchase_history.short_description = 'Historique d\'achat'

# Configuration personnalisée pour le modèle Category
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'order', 'get_product_count')
    list_editable = ('order',)
    search_fields = ('name',)
    ordering = ('order', 'name')

    def get_product_count(self, obj):
        return obj.products.count()
    get_product_count.short_description = 'Nombre de produits'

# Configuration personnalisée pour le modèle Payment
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'amount', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)

# Enregistrement des modèles avec leurs configurations personnalisées
admin.site.register(User, CustomUserAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Review)
admin.site.register(SupportTicket)
admin.site.register(Record)
