# Application Web de Gestion de Location d'Appartements

Une application web complète pour la location d'appartements entre particuliers, développée avec Django, HTML, CSS et MySQL.

## Fonctionnalités

### Utilisateurs
- **Administrateur**: gestion des utilisateurs, validation des appartements, gestion des réservations
- **Propriétaire**: publier/modifier/supprimer des appartements, gérer les réservations
- **Client**: rechercher des logements, effectuer des réservations, messagerie

### Modules Principaux

1. **Gestion des utilisateurs**
   - Inscription avec choix du rôle (propriétaire/client)
   - Connexion/déconnexion
   - Gestion du profil

2. **Gestion des appartements**
   - Ajout, modification, suppression
   - Validation par l'administrateur
   - Recherche par ville, prix, date

3. **Gestion des réservations**
   - Création, modification, annulation
   - Historique des réservations
   - Calcul automatique du montant total

4. **Messagerie**
   - Communication propriétaire-client
   - Notifications en temps réel

## Installation

### Prérequis
- Python 3.8+
- MySQL 5.7+
- pip

### Étapes d'installation

1. **Installer les dépendances**
```bash
pip install django mysqlclient
```

2. **Configurer la base de données MySQL**
```sql
CREATE DATABASE location_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

3. **Configurer les paramètres de connexion**
Modifier `location_app/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'location_db',
        'USER': 'votre_utilisateur',
        'PASSWORD': 'votre_mot_de_passe',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

4. **Créer les tables**
```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Créer un superutilisateur (admin)**
```bash
python manage.py createsuperuser
```

6. **Lancer le serveur**
```bash
python manage.py runserver
```

L'application est accessible à: http://127.0.0.1:8000/

## Structure du projet

```
/workspace/
├── core/                   # Application principale
│   ├── models.py          # Modèles de données
│   ├── views.py           # Vues et logique métier
│   ├── forms.py           # Formulaires
│   └── admin.py           # Configuration admin
├── location_app/          # Configuration du projet
│   ├── settings.py        # Paramètres Django
│   └── urls.py            # URLs principales
├── templates/             # Templates HTML
│   ├── base.html          # Template de base
│   └── core/              # Templates de l'application
├── static/                # Fichiers statiques
│   └── css/
│       └── style.css      # Styles CSS
└── media/                 # Fichiers uploadés
```

## Utilisation

1. **Inscription**: Créez un compte en choisissant votre rôle (propriétaire ou client)
2. **Propriétaire**: Publiez vos appartements et attendez la validation de l'admin
3. **Client**: Recherchez et réservez des appartements
4. **Admin**: Validez les appartements et gérez les utilisateurs via l'interface d'administration (/admin/)

## Technologies

- **Backend**: Django 6.0
- **Base de données**: MySQL
- **Frontend**: HTML5, CSS3
- **Authentification**: Django Auth avec modèle utilisateur personnalisé

## Licence

MIT License
