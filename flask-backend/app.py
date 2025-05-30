# Imports nécessaires
from flask import Flask, request, jsonify
from pymongo import MongoClient
from dotenv import load_dotenv
from bson import json_util, ObjectId
from flask_cors import CORS
import json
import os
import re
from bson.objectid import ObjectId

# Chargement des variables d'environnement
load_dotenv()
mongo_uri = os.getenv("MONGO_CLIENT")

app = Flask(__name__)
CORS(app)  # Active CORS pour permettre les appels entre domaines (utile côté frontend)

# Connexion à MongoDB
client = MongoClient(mongo_uri)
db = client["ville_hotels"]  # Nom de la base de données

# ---------------------------- CRUD BASIQUE ----------------------------

# CREATE : ajout d'un hôtel dans une collection spécifique à une ville et une plateforme
@app.route('/<city>/<platform>', methods=['POST'])
def create_entry(city, platform):
    data = request.json
    data["source"] = platform  # Ajout d'une info sur la plateforme source
    collection_name = f"{city.lower()}_{platform.lower()}"  # Ex : paris_airbnb
    result = db[collection_name].insert_one(data)  # Insertion dans MongoDB
    return jsonify({"_id": str(result.inserted_id)}), 201  # Retourne l'id de l'entrée créée

# READ : récupère tous les hôtels pour une ville et une plateforme
@app.route('/<city>/<platform>', methods=['GET'])
def get_entries(city, platform):
    collection_name = f"{city.lower()}_{platform.lower()}"
    entries = list(db[collection_name].find({}, {'_id': 0}))  # Récupère tous les documents sans l’ID
    return jsonify(entries)

# UPDATE : met à jour un hôtel en fonction de son titre
@app.route('/<city>/<platform>', methods=['PUT'])
def update_entry(city, platform):
    data = request.json
    title = data.get("title")  # Le titre de l'hôtel à mettre à jour
    update_data = data.get("update", {})  # Les données à mettre à jour
    collection_name = f"{city.lower()}_{platform.lower()}"
    result = db[collection_name].update_one({"title": title}, {"$set": update_data})  # Mise à jour
    return jsonify({"matched": result.matched_count, "modified": result.modified_count})

# DELETE : supprime un hôtel en fonction de son titre
@app.route('/<city>/<platform>', methods=['DELETE'])
def delete_entry(city, platform):
    title = request.args.get("title")  # Récupère le titre via les paramètres d'URL
    collection_name = f"{city.lower()}_{platform.lower()}"
    result = db[collection_name].delete_one({"title": title})
    return jsonify({"deleted": result.deleted_count})

# Récupère tous les hôtels pour une plateforme donnée, toutes villes confondues
@app.route('/all/<platform>', methods=['GET'])
def get_all_entries(platform):
    all_hotels = []
    collections = [col for col in db.list_collection_names() if col.endswith(f"_{platform.lower()}")]
    for collection in collections:
        hotels = list(db[collection].find({}, {'_id': 0}))
        city = collection.split('_')[0]  # Déduit la ville depuis le nom de la collection
        for hotel in hotels:
            hotel['city'] = city
        all_hotels.extend(hotels)
    return jsonify(all_hotels)

# ---------------------------- SMART SEARCH ----------------------------

# Recherche multi-critères avancée (prix, score, distance, mot-clé dans le titre, pagination, tri)
@app.route("/smart-search", methods=["GET"])
def smart_search():
    # Paramètres de filtrage
    sources = request.args.getlist("source") or ["airbnb", "booking", "hotelscom"]
    cities = request.args.getlist("city") or ["paris", "berlin", "london", "madrid", "rome"]

    # Validation des valeurs
    valid_sources = {"airbnb", "booking", "hotelscom"}
    valid_cities = {"paris", "berlin", "london", "madrid", "rome"}
    if not all(src in valid_sources for src in sources):
        return jsonify({"error": f"Invalid source. Must be in {', '.join(valid_sources)}"}), 400
    if not all(city.lower() in valid_cities for city in cities):
        return jsonify({"error": f"Invalid city. Must be in {', '.join(valid_cities)}"}), 400

    # Extraction des filtres
    min_price = request.args.get("min_price", type=float)
    max_price = request.args.get("max_price", type=float)
    min_score = request.args.get("min_score", type=float)
    max_distance = request.args.get("max_distance", type=float)
    title_contains = request.args.get("title_contains")
    offset = request.args.get("offset", default=0, type=int)
    limit = request.args.get("limit", default=20, type=int)
    sort_by = request.args.get("sort_by", "rating")
    sort_order = int(request.args.get("sort_order", -1))

    all_results = []

    # Boucle sur chaque combinaison ville / source
    for city in cities:
        for source in sources:
            coll_name = f"{city.lower()}_{source}"
            if coll_name not in db.list_collection_names():
                continue
            collection = db[coll_name]

            rating_expr = "$rating" if source == "airbnb" else "$rating.score"
            pipeline = []

            # Ajoute des champs unifiés pour faciliter la recherche
            pipeline.append({
                "$addFields": {
                    "unified_rating": {"$cond": [{"$isNumber": rating_expr}, rating_expr, None]},
                    "unified_price": "$price.value",
                    "unified_distance": "$distanceFromCenter" if source == "booking" else None,
                    "source": {"$literal": source},
                    "city": {"$literal": city}
                }
            })

            # Filtrage selon les critères fournis
            match = {}
            if min_price is not None or max_price is not None:
                match["unified_price"] = {}
                if min_price is not None:
                    match["unified_price"]["$gte"] = min_price
                if max_price is not None:
                    match["unified_price"]["$lte"] = max_price
            if min_score is not None:
                match["unified_rating"] = {"$gte": min_score}
            if max_distance is not None:
                match["unified_distance"] = {"$lte": max_distance}
            if title_contains:
                match["title"] = {"$regex": title_contains, "$options": "i"}
            if match:
                pipeline.append({"$match": match})

            # Projection finale
            pipeline.append({
                "$project": {
                    "_id": 0,
                    "title": 1,
                    "thumbnail": 1,
                    "link": 1,
                    "location": 1,
                    "unified_price": 1,
                    "unified_rating": 1,
                    "unified_distance": 1,
                    "source": 1,
                    "city": 1
                }
            })

            results = list(collection.aggregate(pipeline))
            all_results.extend(results)

    # Tri
    sort_key_map = {"rating": "unified_rating", "price": "unified_price", "distance": "unified_distance"}
    sort_key = sort_key_map.get(sort_by, "unified_rating")
    all_results = [r for r in all_results if r.get(sort_key) is not None]
    all_results.sort(key=lambda x: x.get(sort_key), reverse=(sort_order == -1))

    # Pagination
    paginated = all_results[offset:offset + limit]

    return jsonify({
        "results": paginated,
        "total": len(all_results)
    })

# ---------------------------- VALUE SCORE ----------------------------

# Score qualité-prix : rapport entre note et prix normalisés
@app.route("/value-score", methods=["GET"])
def value_score():
    city_param = request.args.get("city")
    source_param = request.args.get("source")
    cities = [city_param.lower()] if city_param else ALL_CITIES
    sources = [source_param.lower()] if source_param else ALL_SOURCES

    all_results = []

    for city in cities:
        for source in sources:
            collection_name = f"{city}_{source}"
            if collection_name not in db.list_collection_names():
                continue
            collection = db[collection_name]

            rating_expr = "$rating" if source == "airbnb" else "$rating.score"
            price_expr = "$price.value"

            # Étape 1 : calcul des min / max pour normalisation
            stats_pipeline = [
                {
                    "$addFields": {
                        "unified_rating": {"$convert": {"input": rating_expr, "to": "double", "onError": None, "onNull": None}},
                        "unified_price": {"$convert": {"input": price_expr, "to": "double", "onError": None, "onNull": None}}
                    }
                },
                {
                    "$match": {"unified_rating": {"$ne": None}, "unified_price": {"$gt": 0}}
                },
                {
                    "$group": {
                        "_id": None,
                        "rating_min": {"$min": "$unified_rating"},
                        "rating_max": {"$max": "$unified_rating"},
                        "price_min": {"$min": "$unified_price"},
                        "price_max": {"$max": "$unified_price"}
                    }
                }
            ]
            stats_result = list(collection.aggregate(stats_pipeline))
            if not stats_result:
                continue
            stats = stats_result[0]

            # Étape 2 : pipeline principal pour calcul du value_score
            pipeline = [
                {
                    "$addFields": {
                        "unified_rating": {"$convert": {"input": rating_expr, "to": "double", "onError": None, "onNull": None}},
                        "unified_price": {"$convert": {"input": price_expr, "to": "double", "onError": None, "onNull": None}}
                    }
                },
                {
                    "$match": {"unified_rating": {"$ne": None}, "unified_price": {"$gt": 0}}
                },
                {
                    "$addFields": {
                        "normalized_rating": {
                            "$cond": [
                                {"$eq": [stats["rating_max"], stats["rating_min"]]},
                                1,
                                {"$divide": [{"$subtract": ["$unified_rating", stats["rating_min"]]}, stats["rating_max"] - stats["rating_min"]]}
                            ]
                        },
                        "normalized_price": {
                            "$cond": [
                                {"$eq": [stats["price_max"], stats["price_min"]]},
                                1,
                                {"$divide": [{"$subtract": ["$unified_price", stats["price_min"]]}, stats["price_max"] - stats["price_min"]]}
                            ]
                        }
                    }
                },
                {
                    "$addFields": {
                        "value_score": {"$subtract": ["$normalized_rating", "$normalized_price"]}
                    }
                },
                {"$sort": {"value_score": -1}},
                {"$limit": 20},
                {
                    "$project": {
                        "_id": 1,
                        "title": 1,
                        "thumbnail": 1,
                        "link": 1,
                        "location": 1,
                        "unified_price": 1,
                        "unified_rating": 1,
                        "value_score": 1,
                        "city": {"$literal": city},
                        "source": {"$literal": source}
                    }
                }
            ]
            results = list(collection.aggregate(pipeline))
            all_results.extend(results)

    # Conversion des ObjectId en chaînes
    for item in all_results:
        if "_id" in item and isinstance(item["_id"], ObjectId):
            item["_id"] = str(item["_id"])
    return jsonify(all_results)

# ---------------------------- COMMENTAIRES ----------------------------

# Ajout d'un commentaire utilisateur sur un hôtel
@app.route('/comment', methods=['POST'])
def add_comment():
    data = request.json
    city = data.get("city")
    platform = data.get("platform")
    title = data.get("title")
    comment = {
        "comment": data.get("comment"),
        "rating": data.get("rating"),
        "user": data.get("user")
    }
    db["comments"].insert_one({
        "city": city,
        "platform": platform,
        "title": title,
        **comment
    })
    return jsonify({"message": "Comment added successfully"})

# Récupère les commentaires filtrés par ville, plateforme ou titre
@app.route('/comments', methods=['GET'])
def get_comments():
    city = request.args.get("city")
    platform = request.args.get("platform")
    title = request.args.get("title")
    query = {}
    if city: query["city"] = city
    if platform: query["platform"] = platform
    if title: query["title"] = title
    comments = list(db["comments"].find(query, {"_id": 0}))
    return jsonify(comments)

# ---------------------------- FAVORIS ----------------------------

# Ajout d’un hôtel aux favoris d’un utilisateur
@app.route('/favorites', methods=['POST'])
def add_favorite():
    data = request.json
    favorite = {
        "user": data.get("user"),
        "city": data.get("city"),
        "platform": data.get("platform"),
        "title": data.get("title")
    }
    db["favorites"].insert_one(favorite)
    return jsonify({"message": "Hotel added to favorites"})

# Récupère les favoris d’un utilisateur
@app.route('/favorites', methods=['GET'])
def get_favorites():
    user = request.args.get("user")
    if not user:
        return jsonify({"error": "User is required"}), 400
    favorites = list(db["favorites"].find({"user": user}, {"_id": 0}))
    return jsonify(favorites)

# Suppression d’un hôtel des favoris
@app.route('/favorites', methods=['DELETE'])
def delete_favorite():
    data = request.json
    user = data.get("user")
    title = data.get("title")
    result = db["favorites"].delete_one({"user": user, "title": title})
    return jsonify({"deleted": result.deleted_count})

# ---------------------------- MAIN ----------------------------

# Lancement du serveur Flask
if __name__ == '__main__':
    app.run(debug=True)