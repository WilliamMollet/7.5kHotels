from flask import Flask, request, jsonify
from pymongo import MongoClient
from dotenv import load_dotenv
from bson import json_util, ObjectId
from flask_cors import CORS
import json
import os
import re
from bson.objectid import ObjectId

load_dotenv()
mongo_uri = os.getenv("MONGO_CLIENT")

app = Flask(__name__)
CORS(app)  # Activer CORS pour toutes les routes

client = MongoClient(mongo_uri)
db = client["ville_hotels"]

# CREATE
@app.route('/<city>/<platform>', methods=['POST'])
def create_entry(city, platform):
    data = request.json
    data["source"] = platform  # Ajouter une info sur la provenance
    collection_name = f"{city.lower()}_{platform.lower()}"
    result = db[collection_name].insert_one(data)
    return jsonify({"_id": str(result.inserted_id)}), 201

# READ
@app.route('/<city>/<platform>', methods=['GET'])
def get_entries(city, platform):
    collection_name = f"{city.lower()}_{platform.lower()}"
    entries = list(db[collection_name].find({}, {'_id': 0}))
    return jsonify(entries)

# UPDATE
@app.route('/<city>/<platform>', methods=['PUT'])
def update_entry(city, platform):
    data = request.json
    title = data.get("title")
    update_data = data.get("update", {})
    collection_name = f"{city.lower()}_{platform.lower()}"
    result = db[collection_name].update_one({"title": title}, {"$set": update_data})
    return jsonify({"matched": result.matched_count, "modified": result.modified_count})

# DELETE
@app.route('/<city>/<platform>', methods=['DELETE'])
def delete_entry(city, platform):
    title = request.args.get("title")
    collection_name = f"{city.lower()}_{platform.lower()}"
    result = db[collection_name].delete_one({"title": title})
    return jsonify({"deleted": result.deleted_count})

# Nouvelle route pour récupérer tous les hôtels
@app.route('/all/<platform>', methods=['GET'])
def get_all_entries(platform):
    all_hotels = []
    # Récupérer toutes les collections qui correspondent à la plateforme
    collections = [col for col in db.list_collection_names() if col.endswith(f"_{platform.lower()}")]
    
    for collection in collections:
        hotels = list(db[collection].find({}, {'_id': 0}))
        # Ajouter la ville à chaque hôtel
        city = collection.split('_')[0]
        for hotel in hotels:
            hotel['city'] = city
        all_hotels.extend(hotels)
    
    return jsonify(all_hotels)

def get_collection(city, source):
    return db[f"{city.lower()}_{source.lower()}"]

@app.route("/smart-search", methods=["GET"])
def smart_search():
    # Paramètres multiples
    sources = request.args.getlist("source") or ["airbnb", "booking", "hotelscom"]
    cities = request.args.getlist("city") or ["paris", "berlin", "london", "madrid", "rome"]

    valid_sources = {"airbnb", "booking", "hotelscom"}
    valid_cities = {"paris", "berlin", "london", "madrid", "rome"}

    # Validation
    if not all(src in valid_sources for src in sources):
        return jsonify({"error": f"Invalid source. Must be in {', '.join(valid_sources)}"}), 400
    if not all(city.lower() in valid_cities for city in cities):
        return jsonify({"error": f"Invalid city. Must be in {', '.join(valid_cities)}"}), 400

    # Filtres
    min_price = request.args.get("min_price", type=float)
    max_price = request.args.get("max_price", type=float)
    min_score = request.args.get("min_score", type=float)
    max_distance = request.args.get("max_distance", type=float)
    title_contains = request.args.get("title_contains")

    sort_by = request.args.get("sort_by", "rating")
    sort_order = int(request.args.get("sort_order", -1))

    all_results = []

    for city in cities:
        for source in sources:
            coll_name = f"{city.lower()}_{source}"
            if coll_name not in db.list_collection_names():
                continue
            collection = db[coll_name]

            rating_expr = "$rating" if source == "airbnb" else "$rating.score"
            pipeline = []

            pipeline.append({
                "$addFields": {
                    "unified_rating": {
                        "$cond": [{"$isNumber": rating_expr}, rating_expr, None]
                    },
                    "unified_price": "$price.value",
                    "unified_distance": "$distanceFromCenter" if source == "booking" else None,
                    "source": {"$literal": source},
                    "city": {"$literal": city}
                }
            })

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
    sort_key_map = {
        "rating": "unified_rating",
        "price": "unified_price",
        "distance": "unified_distance"
    }
    sort_key = sort_key_map.get(sort_by, "unified_rating")
    all_results = [r for r in all_results if r.get(sort_key) is not None]
    all_results.sort(key=lambda x: x.get(sort_key), reverse=(sort_order == -1))

    return jsonify(all_results[:20])

# Config
ALL_CITIES = ["paris", "berlin", "london", "madrid", "rome"]
ALL_SOURCES = ["airbnb", "booking", "hotelscom"]

@app.route("/value-score", methods=["GET"])
def value_score():
    city_param = request.args.get("city")
    source_param = request.args.get("source")

    # Liste des combinaisons à traiter
    cities = [city_param.lower()] if city_param else ALL_CITIES
    sources = [source_param.lower()] if source_param else ALL_SOURCES

    all_results = []

    for city in cities:
        for source in sources:
            collection_name = f"{city}_{source}"
            if collection_name not in db.list_collection_names():
                continue  # Skip si la collection n'existe pas
            collection = db[collection_name]

            rating_expr = "$rating" if source == "airbnb" else "$rating.score"
            price_expr = "$price.value"

            # 1. Statistiques de base
            stats_pipeline = [
                {
                    "$addFields": {
                        "unified_rating": {
                            "$convert": {
                                "input": rating_expr,
                                "to": "double",
                                "onError": None,
                                "onNull": None
                            }
                        },
                        "unified_price": {
                            "$convert": {
                                "input": price_expr,
                                "to": "double",
                                "onError": None,
                                "onNull": None
                            }
                        }
                    }
                },
                {
                    "$match": {
                        "unified_rating": {"$ne": None},
                        "unified_price": {"$gt": 0}
                    }
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

            # 2. Pipeline principal
            pipeline = [
                {
                    "$addFields": {
                        "unified_rating": {
                            "$convert": {
                                "input": rating_expr,
                                "to": "double",
                                "onError": None,
                                "onNull": None
                            }
                        },
                        "unified_price": {
                            "$convert": {
                                "input": price_expr,
                                "to": "double",
                                "onError": None,
                                "onNull": None
                            }
                        }
                    }
                },
                {
                    "$match": {
                        "unified_rating": {"$ne": None},
                        "unified_price": {"$gt": 0}
                    }
                },
                {
                    "$addFields": {
                        "normalized_rating": {
                            "$cond": [
                                {"$eq": [stats["rating_max"], stats["rating_min"]]},
                                1,
                                {
                                    "$divide": [
                                        {"$subtract": ["$unified_rating", stats["rating_min"]]},
                                        stats["rating_max"] - stats["rating_min"]
                                    ]
                                }
                            ]
                        },
                        "normalized_price": {
                            "$cond": [
                                {"$eq": [stats["price_max"], stats["price_min"]]},
                                1,
                                {
                                    "$divide": [
                                        {"$subtract": ["$unified_price", stats["price_min"]]},
                                        stats["price_max"] - stats["price_min"]
                                    ]
                                }
                            ]
                        }
                    }
                },
                {
                    "$addFields": {
                        "value_score": {
                            "$subtract": ["$normalized_rating", "$normalized_price"]
                        }
                    }
                },
                {
                    "$sort": {"value_score": -1}
                },
                {
                    "$limit": 20
                },
                {
                    "$project": {
                        "_id": 1,  # Inclure l'id
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

    for item in all_results:
        if "_id" in item and isinstance(item["_id"], ObjectId):
            item["_id"] = str(item["_id"])
    return jsonify(all_results)



if __name__ == '__main__':
    app.run(debug=True)
