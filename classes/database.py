from pymongo import MongoClient
from dotenv import load_dotenv
import certifi
import os

class Database:

    def __init__(self):
        load_dotenv()
        self.__MONGO_URI = os.getenv("BD_URI")
        self.__DB_NAME = "sample_mflix"  # Nom de la base de données
        self.__COLLECTION_NAME = "job"
        self.__collection = None
        
        self.__mongo()

    def __mongo(self):
        
        while self.__collection is None:
        
            try:
                client = MongoClient(self.__MONGO_URI,tlsCAFile=certifi.where())
                db = client[self.__DB_NAME]
                collection=db[self.__COLLECTION_NAME]
                
                # Vérifier si la connexion fonctionne
                print("✅ Connexion réussie à MongoDB !")
                
                # Vérifie si la collection existe déjà
                if "job" not in db.list_collection_names():
                    db.create_collection("job")
                    print("📁 Collection 'job' créée.")

                #return db["job"]
                self.__collection = collection
            except Exception as e:
                    print(f"❌ Erreur de connexion à MongoDB : {e}")
                    
                    
    def connect_mongo(self):
        return self.__collection
    
   
