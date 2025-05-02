from django.db import migrations

def create_initial_categories_and_products(apps, schema_editor):
    Category = apps.get_model('website', 'Category')
    Product = apps.get_model('website', 'Product')

    # Create Categories
    streaming_video = Category.objects.create(
        id=1,
        name='Streaming Vidéo',
        icon='fas fa-tv',
        description='Services de streaming vidéo',
        order=1
    )

    music = Category.objects.create(
        id=2,
        name='Musique',
        icon='fas fa-music',
        description='Services de streaming musical',
        order=2
    )

    gaming = Category.objects.create(
        id=3,
        name='Gaming',
        icon='fas fa-gamepad',
        description='Services de gaming',
        order=3
    )

    anime = Category.objects.create(
        id=4,
        name='Anime',
        icon='fas fa-dragon',
        description='Services de streaming d\'anime',
        order=4
    )

    # Create Products for Streaming Video
    Product.objects.create(
        id=1,
        name='Netflix',
        category=streaming_video,
        description='Le leader du streaming vidéo avec une large sélection de films et séries.',
        price=14.99,
        features='''- Accès à tous les contenus Netflix
- Streaming en 4K
- Téléchargement pour visionnage hors ligne
- Jusqu'à 4 écrans simultanés''',
        order=1
    )

    Product.objects.create(
        id=2,
        name='Disney+',
        category=streaming_video,
        description='Tous vos films et séries Disney, Marvel, Star Wars et plus encore.',
        price=8.99,
        features='''- Contenu Disney, Marvel, Star Wars
- Streaming en 4K
- Téléchargement disponible
- Jusqu'à 4 écrans simultanés''',
        order=2
    )

    Product.objects.create(
        id=3,
        name='HBO Max',
        category=streaming_video,
        description='Les meilleures séries HBO et plus encore.',
        price=9.99,
        features='''- Séries HBO exclusives
- Films Warner Bros
- Contenu DC Comics
- Streaming en 4K''',
        order=3
    )

    Product.objects.create(
        id=4,
        name='Amazon Prime Video',
        category=streaming_video,
        description='Films et séries inclus avec Amazon Prime.',
        price=5.99,
        features='''- Contenu Prime Video
- Livraison Amazon Prime
- Streaming en 4K
- Téléchargement disponible''',
        order=4
    )

    Product.objects.create(
        id=5,
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
        id=6,
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
        id=7,
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
        id=8,
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

    # Create Products for Music
    Product.objects.create(
        id=9,
        name='Spotify Premium',
        category=music,
        description='Écoutez votre musique sans publicités et en haute qualité.',
        price=9.99,
        features='''- Écoute sans publicités
- Qualité audio élevée
- Téléchargement disponible
- Mode hors ligne''',
        order=1
    )

    Product.objects.create(
        id=10,
        name='Apple Music',
        category=music,
        description='Accédez à plus de 100 millions de titres.',
        price=9.99,
        features='''- Catalogue complet
- Qualité audio lossless
- Téléchargement disponible
- Intégration avec l'écosystème Apple''',
        order=2
    )

    Product.objects.create(
        id=11,
        name='YouTube Music Premium',
        category=music,
        description='Musique et vidéos sans publicités.',
        price=9.99,
        features='''- Écoute sans publicités
- Mode hors ligne
- Téléchargement disponible
- Accès à YouTube Premium''',
        order=3
    )

    # Create Products for Gaming
    Product.objects.create(
        id=12,
        name='Xbox Game Pass',
        category=gaming,
        description='Accès à plus de 100 jeux Xbox.',
        price=14.99,
        features='''- Plus de 100 jeux
- Jeux day one
- Xbox Live Gold inclus
- Jeux sur console et PC''',
        order=1
    )

    Product.objects.create(
        id=13,
        name='PlayStation Plus',
        category=gaming,
        description='Jeux en ligne et jeux mensuels gratuits.',
        price=9.99,
        features='''- Jeux en ligne
- Jeux mensuels gratuits
- Stockage cloud
- Offres exclusives''',
        order=2
    )

    Product.objects.create(
        id=14,
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
        id=15,
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

    # Create Products for Anime
    Product.objects.create(
        id=16,
        name='Crunchyroll Premium',
        category=anime,
        description='Le meilleur du streaming d\'anime.',
        price=7.99,
        features='''- Simulcast
- Sans publicités
- Manga numérique
- Mode hors ligne''',
        order=1
    )

def remove_initial_categories_and_products(apps, schema_editor):
    Category = apps.get_model('website', 'Category')
    Category.objects.all().delete()

class Migration(migrations.Migration):

    dependencies = [
        ('website', '0004_auto_20250502_1116'),
    ]

    operations = [
        migrations.RunPython(create_initial_categories_and_products, remove_initial_categories_and_products),
    ] 