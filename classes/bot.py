import telebot  # Bibliothèque pour créer un bot Telegram
from classes.database import Database  # Module personnalisé pour interagir avec la base de données MongoDB
import os  # Pour accéder aux variables d'environnement
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton  # Pour créer des boutons inline
import time  # Pour gérer les délais
from dotenv import load_dotenv  # Pour charger les variables d'environnement depuis un fichier .env
import html  # Pour échapper les caractères HTML dans les messages
from apscheduler.schedulers.background import BackgroundScheduler  # Planificateur en arrière-plan
from datetime import datetime  # Pour manipuler les dates et heures
from bson import ObjectId  # Pour traiter les IDs MongoDB


class Bot:
    """
    Classe principale pour gérer le bot Telegram.
    """

    def __init__(self):
        """
        Initialisation du bot :
        - Chargement des variables d'environnement.
        - Initialisation du bot Telegram.
        - Configuration des gestionnaires de commandes.
        - Configuration du planificateur pour vérifier les nouvelles offres d'emploi.
        """
        load_dotenv()  # Charge les variables d'environnement depuis le fichier .env
        self.__bot = None  # Instance du bot Telegram (initialisée dans __init_bot)
        self.__collection = Database().connect_mongo()  # Connexion à la collection MongoDB
        self.__user_positions = {}  # Suivi de la position de l'utilisateur dans la pagination
        self.__subscribers = set()  # Ensemble des abonnés recevant des notifications
        self.__last_checked_time = datetime.utcnow()  # Horodatage de la dernière vérification
        self.__sent_jobs = {}  # Stocker les offres déjà envoyées {user_id: set(job_ids)}
        self.__last_messages = {}  # Stocker le dernier message envoyé par utilisateur


        self.__init_bot()  # Initialisation du bot Telegram
        self.__setup_handler()  # Configuration des gestionnaires de commandes
        self.__setup_scheduler()  # Configuration du planificateur pour les vérifications automatiques

    def __init_bot(self):
        """
        Initialise le bot Telegram avec le token fourni dans les variables d'environnement.
        En cas d'échec, réessaie jusqu'à ce que le bot soit initialisé correctement.
        """
        TOKEN = os.getenv('BOT_TOKEN')  # Récupère le token du bot depuis les variables d'environnement
        while self.__bot is None:  # Boucle jusqu'à ce que le bot soit initialisé
            try:
                self.__bot = telebot.TeleBot(TOKEN)
            except Exception as e:
                print(f"🚨 Erreur lors de l'initialisation du bot : {e}")
                time.sleep(5)  # Attente avant de réessayer
    
    def __setup_handler(self):
        """
        Configure les gestionnaires de commandes pour interagir avec les utilisateurs.
        """

        @self.__bot.message_handler(commands=['start', 'hello'])
        def start(message):
            """
            Gestionnaire pour les commandes /start et /hello.
            Affiche les commandes disponibles au nouvel utilisateur.
            """
            
            #Nettoyer l'historique des offres envoyés à cet utilisateur.
            db = Database().connect_mongo()
            sent_jobs_collection = db["sent_jobs"]
            
            sent_jobs_collection.delete_many({"user_id":message.chat.id})
            
            commands_info = (
                "<b>Bienvenu !!</b>\n\n"
                "<b>Voici les commandes disponibles :</b>\n\n"
                "/start - Démarrer le bot de zéro pour recevoir à nouveau toutes les offres.\n"
                "/jobs - Lancer les offres d'emploi\n"
                "/subscribe - Recevoir les nouvelles offres\n"
                "/unsubscribe - Arrêter les notifications"
            )
            print(commands_info)  # DEBUG : Vérifie ce qui est envoyé
            self.__bot.send_message(
                message.chat.id,
                commands_info,
                parse_mode="HTML"  # Utilise le format HTML pour le texte
            )

        @self.__bot.message_handler(commands=['subscribe'])
        def subscribe(message):
            """
            Gestionnaire pour la commande /subscribe.
            Ajoute l'utilisateur à la liste des abonnés pour recevoir des notifications.
            """
            self.__subscribers.add(message.chat.id)
            self.__bot.send_message(message.chat.id, "✅ Vous êtes abonné aux notifications d'offres d'emploi !")

        @self.__bot.message_handler(commands=['unsubscribe'])
        def unsubscribe(message):
            """
            Gestionnaire pour la commande /unsubscribe.
            Supprime l'utilisateur de la liste des abonnés.
            """
            self.__subscribers.discard(message.chat.id)
            self.__bot.send_message(message.chat.id, "❌ Vous êtes désabonné des notifications.")

        @self.__bot.message_handler(commands=['jobs'])
        def send_jobs(message, page=0):
            """
            Gestionnaire pour la commande /jobs.
            Affiche une liste paginée des offres d'emploi stockées dans la base de données.
            """
            if self.__collection is None:
                self.__bot.send_message(
                    message.chat.id,
                    "❌ Erreur de connexion à la base de données.",
                    parse_mode="HTML"
                )
                return

            # Récupère 10 offres par page
            jobs = list(self.__collection.find())
            if not jobs:
                self.__bot.send_message(
                    message.chat.id,
                    "Aucune offre disponible pour le moment.",
                    parse_mode="HTML"
                )
                return

            # Mémorise la page actuelle pour l'utilisateur
            self.__user_positions[message.chat.id] = page
            
             # Vérifier si l'utilisateur a déjà reçu une offre spécifique
            db = Database().connect_mongo()
            sent_jobs_collection = db["sent_jobs"]

            for job in jobs:
                
                 # Vérifier si cette offre a déjà été envoyée à cet utilisateur
                if sent_jobs_collection.find_one({"user_id": message.chat.id, "job_id": job["_id"]}):
                 continue  # Passer cette offre car elle a déjà été envoyée

                self.__send_job_message(message.chat.id, job)
                 # Enregistrer cette offre comme envoyée pour cet utilisateur
                sent_jobs_collection.insert_one({"user_id": message.chat.id, "job_id": job["_id"], "timestamp": datetime.utcnow()})

       
    def __send_job_message(self, chat_id, job):
        """
        Envoie un message contenant les détails d'une offre d'emploi à un utilisateur.
        """
        job_id = str(job["_id"])  # Convertir l'ID en string
    
        # Vérifier si l'utilisateur a déjà reçu cette offre
        if chat_id in self.__sent_jobs and job_id in self.__sent_jobs[chat_id]:
            return  # Ne pas envoyer l'offre en double
        
        # Ajouter le job_id dans la liste des messages envoyés
        if chat_id not in self.__sent_jobs:
            self.__sent_jobs[chat_id] = set()
        self.__sent_jobs[chat_id].add(job_id)
        
        # Échappe les caractères spéciaux pour éviter les erreurs HTML
        title = html.escape(str(job.get("Titre du poste") or "N/A"))
        company = html.escape(str(job.get("Nom de l'entreprise") or "N/A"))
        duree = html.escape(str(job.get("Durée") or "N/A"))
        diplome = html.escape(str(job.get("Diplôme requis") or "N/A"))
        experience = html.escape(str(job.get("Expérience") or "N/A"))
        langues = html.escape(str(job.get("Langues") or "N/A"))
        date_limite = html.escape(str(job.get("Date limite candidature") or "N/A"))
        comment_postuler = html.escape(str(job.get("Comment postuler") or "N/A"))
        url = html.escape(str(job.get("url") or "#"))
        
         # Vérifier si l'URL est valide
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://example.com"  # Met une URL par défaut pour éviter les erreurs


        # Construction du message en HTML
        job_text = (
            f"<b>{title}</b>\n"
            f"🏢 <b>Entreprise :</b> {company}\n"
            f"⏳ <b>Durée :</b> {duree}\n"
            f"🎓 <b>Diplôme requis :</b> {diplome}\n"
            f"💼 <b>Expérience :</b> {experience}\n"
            f"🗣 <b>Langues :</b> {langues}\n"
            f"📅 <b>Date limite :</b> {date_limite}\n"
            f"💡 <b>Comment postuler :</b> {comment_postuler}\n"
            f"🔗 <b>Voir plus :</b> <a href='{url}'>Lien de l'offre</a>"
        )

        job_link = job.get('url','#')
        # Bouton "Postuler"
        keyboard = InlineKeyboardMarkup()
        keyboard.add(
            InlineKeyboardButton("📩 Postuler", url=job_link)
        )

        self.__bot.send_message(
            chat_id,
            job_text,
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_markup=keyboard
        )

    def __setup_scheduler(self):
        """
        Configure un planificateur pour vérifier périodiquement les nouvelles offres d'emploi.
        """
        scheduler = BackgroundScheduler()
        scheduler.add_job(self.__check_new_jobs, 'interval', minutes=1)  # Vérifie toutes les minutes
        scheduler.start()

    def __check_new_jobs(self):
        """
        Vérifie si de nouvelles offres d'emploi sont disponibles dans la base de données.
        Si oui, envoie un message à tous les abonnés.
        """
        new_jobs = list(self.__collection.find({"date_publication": {"$gt": self.__last_checked_time}}))

        if new_jobs:
            self.__last_checked_time = datetime.utcnow()  # Met à jour l'horodatage
            for job in new_jobs:
                for user_id in self.__subscribers:
                    self.__send_job_message(user_id, job)

    def launch(self):
        """
        Lance le bot en boucle infinie, avec une gestion des exceptions pour éviter les arrêts inattendus.
        """
        while True:
            try:
                print("Démarrage du bot...")
                self.__bot.polling(none_stop=True, timeout=60, long_polling_timeout=25)
            except Exception as e:
                print(f"🚨 Erreur détectée : {e}")
                time.sleep(5)  # Attend 5 secondes avant de redémarrer
