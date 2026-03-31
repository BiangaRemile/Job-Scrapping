# Job-Scrapping

Bot Telegram de Suivi des Offres d'Emploi

Table des matières Introduction Fonctionnalités Prérequis Installation Utilisation Structure du Projet

Introduction Ce projet consiste en un bot Telegram automatisé qui effectue du web scraping pour récupérer des offres d'emploi à partir d'un site web spécifique. Les descriptions des offres sont ensuite résumées et stockées dans une base de données MongoDB. Le bot envoie ensuite ces informations aux utilisateurs connectés via Telegram.

Le bot utilise plusieurs modules Python pour accomplir ses tâches :

Web Scraping : Pour extraire les données des offres d'emploi. Base de Données : Pour stocker les offres déjà traitées. Telegram Bot API : Pour envoyer les notifications aux utilisateurs.

Fonctionnalités Récupération automatique des offres d'emploi depuis un site web. Vérification si une offre existe déjà dans la base de données pour éviter les doublons. Stockage des offres et de leurs descriptions dans une base de données MongoDB. Envoi des offres nouvelles aux utilisateurs inscrits via Telegram. Exécution parallèle du scrapping et du bot grâce au multithreading.

Prérequis Avant de pouvoir exécuter ce projet, assurez-vous d'avoir les dépendances suivantes installées :

Python 3.8 ou supérieur Pip (gestionnaire de packages Python) MongoDB (base de données NoSQL) Chromedriver (pour Selenium, selon votre version de Chrome)

Bibliothèques Python nécessaires : pip install -r requirements.txt

Installation

Clonez le dépôt GitHub: git clone https://github.com/Mkaj02/MIA_PBL_6B.git cd votre-repo

Installez les dépendances: pip install -r requirements.txt

Utilisation

Lancer le bot python main.py

Ajouter des utilisateurs : Les utilisateurs doivent démarrer une conversation avec le bot Telegram pour recevoir les messages.

Vérifier les logs : Le script affiche des messages de statut dans la console pour indiquer le progrès du scrapping et des insertions dans la base de données.

Structure du Projet /projet-bot-telegram │ ├─- /classes │ ├── scraper.py # Classe pour effectuer le web scraping │ ├── job.py # Classe pour représenter une offre d'emploi │ ├── database.py # Classe pour interagir avec MongoDB │ └── bot.py # Classe pour gérer le bot Telegram │ ├── main.py # Fichier principal pour exécuter le bot et le scrapping ├── .env # Fichier contenant les variables d'environnement ├── requirements.txt # Liste des dépendances Python └── README.md # Documentation du projet

