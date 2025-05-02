from django.db import migrations

def add_missing_services(apps, schema_editor):
    Category = apps.get_model('website', 'Category')
    Product = apps.get_model('website', 'Product')

    # Get existing categories
    streaming_video = Category.objects.get(name='Streaming Vidéo')
    gaming = Category.objects.get(name='Gaming')

    # Add missing streaming video services
    Product.objects.create(
        name='Hulu',
        category=streaming_video,
        description='Séries TV et films populaires.',
        price=7.99,
        features='''- Contenu TV en direct
- Séries exclusives
- Films populaires
- Streaming en HD''',
        order=5
    )

    Product.objects.create(
        name='Apple TV+',
        category=streaming_video,
        description='Contenu original Apple.',
        price=6.99,
        features='''- Contenu original Apple
- Streaming en 4K
- Téléchargement disponible
- Famille jusqu'à 6 personnes''',
        order=6
    )

    Product.objects.create(
        name='Paramount+',
        category=streaming_video,
        description='Films et séries Paramount.',
        price=9.99,
        features='''- Films Paramount
- Séries TV populaires
- Contenu sportif
- Streaming en 4K''',
        order=7
    )

    Product.objects.create(
        name='Peacock',
        category=streaming_video,
        description='Contenu NBC Universal.',
        price=4.99,
        features='''- Contenu NBC
- Films Universal
- Sports en direct
- Streaming en HD''',
        order=8
    )

    # Add missing gaming services
    Product.objects.create(
        name='EA Play',
        category=gaming,
        description='Accès aux jeux EA.',
        price=4.99,
        features='''- Jeux EA populaires
- Contenu exclusif
- Essais anticipés
- Réductions sur les achats''',
        order=3
    )

    Product.objects.create(
        name='Ubisoft+',
        category=gaming,
        description='Accès aux jeux Ubisoft.',
        price=14.99,
        features='''- Catalogue Ubisoft complet
- Jeux day one
- Contenu premium
- Jeux sur PC et console''',
        order=4
    )

def remove_missing_services(apps, schema_editor):
    Product = apps.get_model('website', 'Product')
    Product.objects.filter(name__in=[
        'Hulu', 'Apple TV+', 'Paramount+', 'Peacock', 'EA Play', 'Ubisoft+'
    ]).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('website', '0005_add_initial_categories_and_products'),
    ]

    operations = [
        migrations.RunPython(add_missing_services, remove_missing_services),
    ] 