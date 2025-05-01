# Limitless - Marketplace de comptes premium

Limitless est une marketplace qui permet aux utilisateurs d'acheter des comptes premium pour différents services de streaming, musique, gaming et plus encore.

## Fonctionnalités

- Inscription et authentification des utilisateurs
- Marketplace de comptes premium
- Système de paiement
- Gestion des commandes
- Système d'avis et de notation
- Support client
- Interface d'administration

## Services disponibles

- Streaming Vidéo (Netflix, Disney+, HBO Max, etc.)
- Musique (Spotify, Apple Music, YouTube Music, etc.)
- Gaming (Xbox Game Pass, PlayStation Plus, etc.)
- Et plus encore...

## Installation

1. Clonez le repository :
```bash
git clone https://github.com/mohamedaminebellil/limitless.git
cd limitless
```

2. Créez un environnement virtuel et activez-le :
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Installez les dépendances :
```bash
pip install -r requirements.txt
```

4. Configurez la base de données :
```bash
python manage.py migrate
```

5. Créez un superutilisateur :
```bash
python manage.py createsuperuser
```

6. Lancez le serveur de développement :
```bash
python manage.py runserver
```

## Technologies utilisées

- Django
- MySQL
- Bootstrap
- JavaScript
- HTML/CSS

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou à soumettre une pull request.

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails. 