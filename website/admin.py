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

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'order', 'get_product_count')
    list_editable = ('order',)
    search_fields = ('name', 'description')
    ordering = ('order',)

    def get_product_count(self, obj):
        return obj.products.count()
    get_product_count.short_description = 'Nombre de produits'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'order', 'is_active', 'get_image_preview')
    list_filter = ('category', 'is_active')
    list_editable = ('price', 'is_active', 'order')
    search_fields = ('name', 'description')
    ordering = ('category', 'order')
    readonly_fields = ('get_image_preview',)

    def get_image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px;"/>', obj.image.url)
        return "Pas d'image"
    get_image_preview.short_description = 'Aperçu'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'status', 'created_at', 'price')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'product__name')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username',)
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'service', 'rating', 'created_at')
    list_filter = ('rating', 'service', 'created_at')
    search_fields = ('user__username', 'comment')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ('user', 'subject', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'subject', 'message')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone', 'created')
    search_fields = ('first_name', 'last_name', 'email', 'phone')
    readonly_fields = ('created',)
    ordering = ('-created',)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'balance', 'date_joined')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    readonly_fields = ('date_joined', 'last_login')
    ordering = ('-date_joined',)
    fieldsets = (
        ('Informations personnelles', {
            'fields': ('username', 'email', 'password', 'first_name', 'last_name')
        }),
        ('Profil', {
            'fields': ('role', 'balance', 'profile_photo', 'phone', 'address', 'city')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Dates importantes', {
            'fields': ('last_login', 'date_joined')
        }),
    )
