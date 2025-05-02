from django.db import migrations

def remove_duplicates(apps, schema_editor):
    Product = apps.get_model('website', 'Product')
    
    # Get all product names
    product_names = Product.objects.values_list('name', flat=True).distinct()
    
    # For each product name
    for name in product_names:
        # Get all products with this name, ordered by ID
        products = Product.objects.filter(name=name).order_by('id')
        
        # If there are duplicates
        if products.count() > 1:
            # Keep the first one (lowest ID) and delete the rest
            first_product = products.first()
            products.exclude(id=first_product.id).delete()

def reverse_migration(apps, schema_editor):
    # This migration cannot be reversed
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('website', '0006_add_missing_services'),
    ]

    operations = [
        migrations.RunPython(remove_duplicates, reverse_migration),
    ] 