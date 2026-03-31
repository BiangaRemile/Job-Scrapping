# 🤖 Bot Telegram de Suivi des Offres d'Emploi

> Projet de veille automatisée : scraping d'offres d'emploi, résumé IA, stockage MongoDB et notification via Telegram.

<table>
  <tr>
    <td><strong>👥 Équipe</strong></td>
    <td>
      • Remile Bianga<br>
      • Marie-joyeuse Ampire<br>
      • Orcin Kitwa<br>
      • Simon Wando<br>
      • Miradi Malolo
    </td>
  </tr>
  <tr>
    <td><strong>🎓 Contexte</strong></td>
    <td>Projet étudiant – MIA PBL 6B</td>
  </tr>
  <tr>
    <td><strong>🛠️ Stack</strong></td>
    <td>Python 3.8+, Selenium, MongoDB, Telegram Bot API, Threads</td>
  </tr>
</table>

---

## 📋 Table des matières

1. [Introduction](#-introduction)
2. [Fonctionnalités](#-fonctionnalités)
3. [Prérequis](#-prérequis)
4. [Installation](#-installation)
5. [Configuration](#-configuration)
6. [Utilisation](#-utilisation)
7. [Structure du projet](#-structure-du-projet)
8. [Bonnes pratiques & Sécurité](#-bonnes-pratiques--sécurité)
9. [Dépannage](#-dépannage)
10. [Contribuer](#-contribuer)
---

## 📖 Introduction

Ce projet consiste en un **bot Telegram automatisé** qui effectue du web scraping pour récupérer des offres d'emploi depuis un site web cible. Les descriptions des offres sont ensuite :

- ✅ Résumées via une API d'intelligence artificielle  
- ✅ Stockées dans une base de données **MongoDB** (avec déduplication)  
- ✅ Notifiées aux utilisateurs abonnés via **Telegram**

Le bot s'exécute en **multithreading** pour paralléliser le scraping et l'envoi des messages.

---

## ✨ Fonctionnalités

| Fonctionnalité | Description |
|---------------|-------------|
| 🕷️ Web Scraping | Extraction automatique des offres depuis un site cible (Selenium) |
| 🔍 Dé-duplication | Vérification en base pour éviter les doublons |
| 🧠 Résumé IA | Génération de résumés concis via API externe |
| 💾 Persistance | Stockage structuré dans MongoDB |
| 📢 Notifications | Envoi ciblé aux utilisateurs Telegram abonnés |
| 🧵 Multithreading | Exécution parallèle scraping / bot pour plus de réactivité |
| 🪵 Logs | Suivi détaillé des opérations dans la console |

---

## 🛠️ Prérequis

### Système
- **Python 3.8+**
- **pip** (gestionnaire de packages)
- **MongoDB** (local ou Atlas)
- **Google Chrome + Chromedriver** (versions compatibles)

### Compte Telegram
1. Créer un bot via [@BotFather](https://t.me/BotFather)
2. Récupérer le `BOT_TOKEN`
3. Démarrer une conversation avec votre bot pour l'activer

---

## 🚀 Installation

```bash
# 1. Cloner le dépôt
git clone https://github.com/Mkaj02/MIA_PBL_6B.git
cd MIA_PBL_6B

# 2. Créer un environnement virtuel (recommandé)
python -m venv venv
source venv/bin/activate  # Linux/macOS
# ou
venv\Scripts\activate  # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer les variables d'environnement (voir section suivante)
cp .env.example .env
# → Éditer .env avec vos valeurs réelles

# 5. Lancer le bot
python main.py
```
---
## ⚙️ Configuration
Fichier .env (exemple)
⚠️ Ne commitez jamais ce fichier. Ajoutez-le à .gitignore.

```bash
# Telegram Bot
BOT_TOKEN=votre_bot_token_ici
BOT_LINK=https://t.me/NomDeVotreBot

# API de résumé IA (OpenRouter / DashScope / autre)
AI_API_KEY=votre_cle_api_ia
DASHSCOPE_API_KEY=votre_cle_dashscope

# MongoDB
BD_URI=mongodb+srv://user:pass@cluster.mongodb.net/jobbot?retryWrites=true&w=majority

# (Optionnel) Identifiants cloud supplémentaires
ALIBABA_CLOUD_ID=votre_access_key_id
ALIBABA_CLOUD_SECRET=votre_access_key_secret

```
### Variables requises

| Fonctionnalité | Description | Source |
|---------------|-------------|--------|
|BOT_TOKEN |Token d'authentification du bot Telegram|@BotFather|
|AI_API_KEY |Clé pour l'API de résumé (ex: OpenRouter)|Dashboard fournisseur|
|BD_URI |URI de connexion MongoDB (avec authentification)|MongoDB Atlas / local|
|BOT_LINK |Lien public du bot (optionnel, pour documentation)|@BotFather|

## ▶️ Utilisation
### Lancer l'application
```bash
python main.py
```

### Interagir avec le bot
- Ouvrir Telegram et rechercher @NomDeVotreBot
- Démarrer la conversation avec /start
- Recevoir automatiquement les nouvelles offres détectées

### Monitoring
- Les logs s'affichent en console : progression du scraping, erreurs, insertions DB
- Format : [TIMESTAMP] [MODULE] Message

### Arrêter proprement
```bash
Ctrl+C  # Le bot gère la fermeture des threads et connexions
```
---
## 📁 Structure du projet
```bash
MIA_PBL_6B/
│
├── main.py                 # Point d'entrée : orchestration bot + scraper
├── requirements.txt        # Dépendances Python
├── .env.example            # Modèle de configuration (à copier)
├── .gitignore              # Fichiers à exclure du versionning
├── README.md               # Cette documentation
│
└── classes/
    ├── scraper.py          # Logique de scraping (Selenium)
    ├── job.py              # Modèle de donnée "Offre d'emploi"
    ├── database.py         # Couche d'accès MongoDB (CRUD, déduplication)
    └── bot.py              # Gestionnaire du bot Telegram (handlers, envoi)
```
---
## 🔐 Bonnes pratiques & Sécurité
### ✅ À faire
- Utiliser un .env local et l'ajouter à .gitignore
- Rotation régulière des clés API
- Valider et sanitiser les données scrapées avant stockage
- Logger les erreurs sans exposer de données sensibles
### ❌ À éviter
- Hardcoder des credentials dans le code source
- Exposer la base de données publiquement (restreindre l'accès IP)
- Scraper sans respecter les robots.txt et CGU du site cible

---
## 🛠️ Dépannage
|Problème|Solution possible|
|--------|----------------|
|hromedriver version mismatch | Télécharger la version correspondant à votre Chrome sur chromedriver.chromium.org|
|MongoDB connection timeout| Vérifier l'URI, l'accès réseau, et l'IP whitelist sur Atlas
|Telegram Bot not responding|Confirmer que le bot a été démarré via /start et que le token est correct|
|ModuleNotFoundError|Réinstaller les dépendances : pip install -r requirements.txt|
|Rate limit API IA|Ajouter un délai entre les appels ou vérifier votre quota|

## 🤝 Contribuer
- Forker le dépôt
- Créer une branche : git checkout -b feature/nouvelle-fonctionnalite
- Commiter : git commit -m 'feat: ajout de X'
- Pusher : git push origin feature/nouvelle-fonctionnalite
- Ouvrir une Pull Request

>📝 Merci de respecter les conventions de code et de mettre à jour la documentation si nécessaire.

__Projet réalisé dans le cadre du module MIA PBL 6B – Promotion B2028 2024/2025__
