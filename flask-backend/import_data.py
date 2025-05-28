from pymongo import MongoClient
from dotenv import load_dotenv
import os
import json


load_dotenv()
mongo_uri = os.getenv("MONGO_CLIENT")

# Connexion MongoDB Atlas
client = MongoClient(mongo_uri)
db = client["ville_hotels"]

# Dossier contenant les fichiers JSON (relatif à ce fichier)
folder_path = os.path.join(os.path.dirname(__file__), "cities")

# Parcours des fichiers dans le dossier
for filename in os.listdir(folder_path):
    if filename.endswith(".json"):
        city_name = filename.replace(".json", "")
        file_path = os.path.join(folder_path, filename)

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        airbnb_collection = f"{city_name.lower()}_airbnb"
        booking_collection = f"{city_name.lower()}_booking"
        hotelscom_collection = f"{city_name.lower()}_hotelscom"  # ← ajouté

        if airbnb_collection not in db.list_collection_names():
            airbnb_data = data.get("airbnbHotels", [])
            if airbnb_data:
                db[airbnb_collection].insert_many(airbnb_data)
                print(f"✅ {city_name}: {len(airbnb_data)} logements Airbnb insérés")
        else:
            print(f"⏩ {city_name}: Collection {airbnb_collection} déjà existante")

        if booking_collection not in db.list_collection_names():
            booking_data = data.get("bookingHotels", [])
            if booking_data:
                db[booking_collection].insert_many(booking_data)
                print(f"✅ {city_name}: {len(booking_data)} hôtels Booking insérés")
        else:
            print(f"⏩ {city_name}: Collection {booking_collection} déjà existante")

        # ← ajout du traitement hotelsComHotels
        if hotelscom_collection not in db.list_collection_names():
            hotelscom_data = data.get("hotelsComHotels", [])
            if hotelscom_data:
                db[hotelscom_collection].insert_many(hotelscom_data)
                print(f"✅ {city_name}: {len(hotelscom_data)} hôtels Hotels.com insérés")
        else:
            print(f"⏩ {city_name}: Collection {hotelscom_collection} déjà existante")
