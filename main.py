# Import des classes nécessaires
from classes.scraper import Scraper  # Classe pour effectuer le scrapping des offres d'emploi
from classes.job import Job         # Classe pour représenter un emploi
from classes.database import Database  # Classe pour interagir avec la base de données
from classes.bot import Bot         # Classe pour gérer le bot
from threading import Thread        # Module pour exécuter des fonctions en parallèle

# URL cible pour le scrapping
url = 'https://tonjob.net/'

def scrapping():
    """
    Fonction principale pour le scrapping des offres d'emploi.
    Elle récupère les URLs des offres, vérifie si elles existent déjà dans la base de données,
    et insère les nouvelles offres avec leur description.
    """
    global url
    
    while True:
        # Initialisation du scraper avec l'URL cible
        scraper = Scraper(url)
        
        # Récupération de la liste des URLs des offres d'emploi
        job_list = scraper.get_jobs()
        
        # Si la liste est vide, réessayer jusqu'à ce qu'elle soit remplie
        while not job_list:
            print("\n[SCRAPPING ERROR] Something went wrong... 🔄❌⚠️\n")
            job_list = scraper.get_jobs()

        # Connexion à la base de données et récupération des URLs des offres déjà enregistrées
        list_of_jobs_in_database = [item["url"] for item in Database().connect_mongo().find()]
        
        # Parcours de chaque URL dans la liste des offres d'emploi
        for i, url in enumerate(job_list):
            
            print(f"\n{i}. {url}\n")  # Affichage de l'index et de l'URL de l'offre

            # Variable pour stocker la description de l'offre (initialisée à None)
            description = None
            
            # Vérification si l'URL de l'offre existe déjà dans la base de données
            if url not in list_of_jobs_in_database:
                # Si l'offre n'existe pas, récupérer sa description
                while not description:
                    description = scraper.get_job_description(url)
                
                # Création d'un objet Job avec l'URL et la description
                job = Job(url, description)
                
                # TODO: Insérer le job dans la base de données ici si nécessaire
                # Par exemple : Database().insert_job(job)
            
            else:
                # Si l'offre existe déjà dans la base de données, afficher un message d'information
                print("\n[INFO] Cette offre existe dans la DB... 📝🔍✅\n")

        # Fermeture du navigateur utilisé pour le scrapping
        scraper.driver_quit()

# Instanciation du bot
bot = Bot()

# Création d'un thread pour exécuter la fonction de scrapping en arrière-plan
thread = Thread(target=scrapping)

# Démarrage du thread de scrapping 
thread.start()

# Lancement du bot (le bot s'exécute indépendamment du scrapping grâce au thread)
bot.launch()