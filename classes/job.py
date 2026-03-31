import requests  # Pour effectuer des requêtes HTTP
import json  # Pour manipuler les données JSON
import os  # Pour accéder aux variables d'environnement
import re  # Pour utiliser les expressions régulières
import time  # Pour gérer les délais
from dotenv import load_dotenv  # Pour charger les variables d'environnement depuis un fichier .env
from classes.database import Database  # Module personnalisé pour interagir avec MongoDB
from datetime import date  # Pour manipuler les dates et heures
from dateutil import parser  # Pour analyser et convertir les dates
from classes.script import SCRIPT # Script personnalisé pour guider l'API de résumé


class Job:
    """
    Classe représentant une offre d'emploi.
    Elle extrait les informations nécessaires à partir de la description brute,
    les résume via une API de génération de texte, puis les stocke dans une base de données MongoDB.
    """

    def __init__(self, url: str, data: str):
        """
        Initialisation de l'offre d'emploi :
        - URL de l'offre.
        - Données brutes (description complète).
        - Résumé généré via une API.
        - Extraction des informations clés.
        - Enregistrement dans la base de données.
        """
        self.__url = url  # URL de l'offre
        self.__data = data  # Description brute de l'offre
        self.__summary = None  # Résumé généré par l'API
        self.__description = {}  # Informations extraites du résumé
        self.__database = None  # Instance de connexion à la base de données
        load_dotenv()  # Charge les variables d'environnement depuis le fichier .env

        # Étapes principales :
        self.__summarize()  # Génère un résumé à partir de la description brute
        self.__extract_job_info()  # Extrait les informations pertinentes du résumé
        self.__save()  # Stocke l'offre dans la base de données

    def __summarize(self):
        """
        Génère un résumé structuré à partir de la description brute en utilisant une API de génération de texte.
        """
        while not self.__summary:  # Boucle jusqu'à ce que le résumé soit obtenu
            try:
                response = requests.post(
                    url="https://openrouter.ai/api/v1/chat/completions",  # URL de l'API
                    headers={
                        "Authorization": f"Bearer {os.getenv('AI_API_KEY')}",  # Clé API
                        "Content-Type": "application/json",
                        "HTTP-Referer": os.getenv('BOT_LINK'),  # Facultatif
                        "X-Title": "Job Poster",  # Facultatif
                    },
                    data=json.dumps({
                        "model": "qwen/qwen2.5-vl-72b-instruct:free",  # Modèle utilisé
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": f"{SCRIPT} \n {self.__data}"  # Script + description brute
                                    }
                                ]
                            }
                        ],
                    })
                )
                response_data = response.json()
                data = response_data['choices'][0]["message"]["content"]  # Récupère le contenu généré
                self.__summary = data  # Stocke le résumé
            except Exception as e:
                print("\n[API ERROR] Server de QWEN 2.5 ne répond pas 🚫⚠️\n")
                print("\n[API INFO] Wait 5 minutes, The operation will be launch again... ⏳⏰\n")
                time.sleep(120)  # Attend 2 minutes avant de réessayer

    def __extract_job_info(self):
        """
        Extrait les informations pertinentes du résumé généré en utilisant des expressions régulières.
        """
        # Initialisation du dictionnaire pour stocker les informations
        job_info = {
            "Titre du poste": "",
            "Lieu": "",
            "Nom de l'entreprise": "",
            "Durée": "",
            "Diplôme requis": "",
            "Expérience": "",
            "Langues": "",
            "Date limite candidature": "",
            "Comment postuler": ""
        }

        # Conversion du résumé en lignes pour faciliter l'extraction
        lines = self.__summary.strip().split("\n")

        # Définition des regex pour chaque champ
        patterns = {
            "Titre du poste": r"\*\*(.*?)\*\*",  # Titre entre **
            "Lieu": r"(?:-|–)\s*Lieu\s*:\s*(.*)",  # Gère "- Lieu :" ou "– Lieu :"
            "Nom de l'entreprise": r"Nom de l'entreprise:\s*(.*)",
            "Durée": r"Durée\s*:\s*(.*)",
            "Diplôme requis": r"Diplôme.*?:\s*(.*)",
            "Expérience": r"Expérience\s*:\s*(.*)",
            "Langues": r"Langues\s*:\s*(.*)",
            "Date limite candidature": r"Date limite candidature\s*:\s*(.*)",
            "Comment postuler": r"Comment postuler\s*:\s*(.*)"
        }

        # Parcours des lignes pour extraire les informations avec regex
        for line in lines:
            for key, pattern in patterns.items():
                match = re.search(pattern, line.strip(), re.IGNORECASE)
                if match:
                    job_info[key] = match.group(1).strip()
                    break  # Passe à la ligne suivante après avoir trouvé un match

        # Si le titre du poste est mentionné avant les autres détails, on l'extrait
        if not job_info["Titre du poste"]:
            title_match = re.search(patterns["Titre du poste"], self.__summary, re.IGNORECASE)
            if title_match:
                job_info["Titre du poste"] = title_match.group(1).strip()

        self.__description = job_info  # Stocke les informations extraites

    def __save(self):
        """
        Stocke les informations de l'offre d'emploi dans la base de données MongoDB.
        """
        while self.__database is None:  # Assure la connexion à la base de données
            self.__database = Database().connect_mongo()

        # Préparation des données à insérer
        job = {
            "url": self.__url,
            "Titre du poste": self.__description.get("Titre du poste"),
            "Lieu": self.__description.get("Lieu"),
            "Nom de l'entreprise": self.__description.get("Nom de l'entreprise"),
            "Durée": self.__description.get("Durée"),
            "Diplôme requis": self.__description.get("Diplôme requis"),
            "Expérience": self.__description.get("Expérience"),
            "Langues": self.__description.get("Langues"),
            "Date limite candidature": self.__description.get("Date limite candidature"),
            "Comment postuler": self.__description.get("Comment postuler"),
        }

        # Analyse et validation de la date limite
        date_limite = self.__parse_date(job["Date limite candidature"])

        # Insère uniquement les nouvelles offres valides
        if job["Titre du poste"]:
            if date_limite is None or date_limite >= date.today().isoformat():  # Vérifie si la date est valide ou non spécifiée
                date_limite = date_limite or "Pas spécifié dans l'offre"
                job["Date limite candidature"] = date_limite
                self.__database.insert_one(job)  # Insertion dans la base de données
                print(f"✅ Offre insérée : {job['Titre du poste']} - {job['Nom de l\'entreprise']}")
        else:
            print("Job non inséré... 🚫📝❌")

    def get_description(self) -> dict:
        """
        Retourne les informations extraites de l'offre d'emploi.
        """
        return self.__description

    def __parse_date(self, date_str):
        """
        Essaie de convertir une date sous différents formats en YYYY-MM-DD.
        Retourne None si la date est invalide ou impossible à convertir.
        """
        if not date_str or date_str.lower() in ["non spécifié", "aucune", "n/a", ""]:
            return None  # Si la date n'est pas précisée

        try:
            # Normalisation des séparateurs (remplace les points, slash par des tirets)
            date_str = re.sub(r"[./]", "-", date_str.strip())
            # Essai de conversion automatique avec dateutil.parser
            parsed_date = parser.parse(date_str, dayfirst=True)
            # Retourne la date au format standardisé YYYY-MM-DD
            return parsed_date.strftime("%Y-%m-%d")
        except Exception:
            return None  # Retourne None si la conversion échoue