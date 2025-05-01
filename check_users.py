import os
import sys
import django

# Configurer l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dcrm.settings')
django.setup()

# Importer le modèle User après avoir configuré Django
from website.models import User

def list_all_users():
    """Liste tous les utilisateurs enregistrés dans la base de données"""
    print("\n--- LISTE DES UTILISATEURS ENREGISTRÉS ---\n")
    
    users = User.objects.all()
    
    if not users:
        print("Aucun utilisateur n'est enregistré dans la base de données.")
        return
    
    print(f"Nombre total d'utilisateurs: {users.count()}\n")
    
    for idx, user in enumerate(users, 1):
        print(f"--- Utilisateur {idx} ---")
        print(f"ID: {user.id}")
        print(f"Nom d'utilisateur: {user.username}")
        print(f"Email: {user.email}")
        print(f"Prénom: {user.first_name}")
        print(f"Nom: {user.last_name}")
        print(f"Téléphone: {user.phone}")
        print(f"Adresse: {user.address}")
        print(f"Ville: {user.city}")
        print(f"Date d'inscription: {user.date_joined}")
        print(f"Dernière connexion: {user.last_login}")
        print(f"Rôle: {user.role}")
        print(f"Solde: {user.balance} TND")
        print(f"Photo de profil: {'Oui' if user.profile_photo else 'Non'}")
        print("\n")

def search_user(username_or_email):
    """Recherche un utilisateur par nom d'utilisateur ou email"""
    try:
        # Recherche par nom d'utilisateur
        user = User.objects.filter(username__icontains=username_or_email) | User.objects.filter(email__icontains=username_or_email)
        
        if user:
            print(f"\n--- Résultats de recherche pour '{username_or_email}' ---\n")
            for idx, u in enumerate(user, 1):
                print(f"--- Résultat {idx} ---")
                print(f"ID: {u.id}")
                print(f"Nom d'utilisateur: {u.username}")
                print(f"Email: {u.email}")
                print(f"Prénom: {u.first_name}")
                print(f"Nom: {u.last_name}")
                print(f"Téléphone: {u.phone}")
                print(f"Adresse: {u.address}")
                print(f"Ville: {u.city}")
                print("\n")
        else:
            print(f"\nAucun utilisateur trouvé avec '{username_or_email}'.")
    except Exception as e:
        print(f"Erreur lors de la recherche: {e}")

def display_menu():
    """Affiche le menu principal"""
    print("\n=== VÉRIFICATION DES UTILISATEURS ===")
    print("1. Lister tous les utilisateurs")
    print("2. Rechercher un utilisateur")
    print("3. Quitter")
    choice = input("\nChoisissez une option (1-3): ")
    return choice

def main():
    """Fonction principale"""
    while True:
        choice = display_menu()
        
        if choice == '1':
            list_all_users()
        elif choice == '2':
            search_term = input("\nEntrez un nom d'utilisateur ou email à rechercher: ")
            search_user(search_term)
        elif choice == '3':
            print("\nAu revoir!")
            sys.exit(0)
        else:
            print("\nOption invalide. Veuillez réessayer.")
        
        input("\nAppuyez sur Entrée pour continuer...")

if __name__ == "__main__":
    main() 