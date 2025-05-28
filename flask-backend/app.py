from flask import Flask, request, jsonify
from pymongo import MongoClient
from dotenv import load_dotenv
from flask_cors import CORS
import os

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


def get_collection(city, source):
    return db[f"{city.lower()}_{source.lower()}"]

@app.route("/smart-search", methods=["GET"])
def smart_search():
    city = request.args.get("city")
    source = request.args.get("source")  # airbnb, booking, hotelscom

    if not city or not source:
        return jsonify({"error": "city and source are required"}), 400

    collection = get_collection(city, source)

    # Filtres facultatifs
    min_price = request.args.get("min_price", type=float)
    max_price = request.args.get("max_price", type=float)
    min_score = request.args.get("min_score", type=float)
    max_distance = request.args.get("max_distance", type=float)

    sort_by = request.args.get("sort_by", "rating")  # price, rating, distance
    sort_order = int(request.args.get("sort_order", -1))  # -1 = DESC, 1 = ASC

    pipeline = []

    # Construction du filtre $match
    match_stage = {}

    if min_price or max_price:
        match_stage["price.value"] = {}
        if min_price:
            match_stage["price.value"]["$gte"] = min_price
        if max_price:
            match_stage["price.value"]["$lte"] = max_price

    if min_score:
        match_stage["rating"] = {"$gte": min_score}  # Airbnb
        # ou "rating.score" pour Booking/HotelsCom si structure différente

    if max_distance:
        match_stage["distanceFromCenter"] = {"$lte": max_distance}

    if match_stage:
        pipeline.append({"$match": match_stage})

    # Projection des champs utiles
    pipeline.append({
        "$project": {
            "_id": 0,
            "title": 1,
            "price": 1,
            "rating": 1,
            "location": 1,
            "distanceFromCenter": 1,
            "link": 1,
            "thumbnail": 1
        }
    })

    # Mapping du champ de tri
    sort_fields = {
        "price": "price.value",
        "rating": "rating" if source == "airbnb" else "rating.score",
        "distance": "distanceFromCenter"
    }

    if sort_by in sort_fields:
        pipeline.append({
            "$sort": {sort_fields[sort_by]: sort_order}
        })

    # Limite des résultats
    pipeline.append({"$limit": 20})

    results = list(collection.aggregate(pipeline))
    return jsonify(results)

@app.route("/smart-search-multi", methods=["GET"])
def smart_search_multi():
    city = request.args.get("city")
    if not city:
        return jsonify({"error": "city is required"}), 400

    min_price = request.args.get("min_price", type=float)
    max_price = request.args.get("max_price", type=float)
    min_score = request.args.get("min_score", type=float)
    max_distance = request.args.get("max_distance", type=float)

    sort_by = request.args.get("sort_by", "rating")  # rating, price, distance
    sort_order = int(request.args.get("sort_order", -1))

    sources = ["airbnb", "booking", "hotelscom"]
    all_results = []

    for source in sources:
        try:
            collection = db[f"{city.lower()}_{source}"]
        except:
            continue

        pipeline = []

        # Ajout d’un champ unifié pour le rating (selon la source)
        rating_expr = "$rating" if source == "airbnb" else "$rating.score"

        # Ajout d’un champ unifié et filtrage
        add_fields = {
            "unified_rating": {
                "$cond": [{"$isNumber": rating_expr}, rating_expr, None]
            },
            "unified_price": "$price.value",
            "unified_distance": "$distanceFromCenter",
            "source": {"$literal": source}
        }

        pipeline.append({"$addFields": add_fields})

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

        if match:
            pipeline.append({"$match": match})

        # Project les champs standardisés
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
                "source": 1
            }
        })

        results = list(collection.aggregate(pipeline))
        all_results.extend(results)

    # Tri en Python après agrégation
    sort_key = {
        "rating": "unified_rating",
        "price": "unified_price",
        "distance": "unified_distance"
    }.get(sort_by, "unified_rating")

    all_results = [r for r in all_results if r.get(sort_key) is not None]
    all_results.sort(key=lambda x: x.get(sort_key), reverse=(sort_order == -1))

    return jsonify(all_results[:20])  # Top 20

@app.route("/value-score", methods=["GET"])
def value_score():
    city = request.args.get("city")
    source = request.args.get("source")  # airbnb, booking, hotelscom

    if not city or not source:
        return jsonify({"error": "city and source are required"}), 400

    collection = get_collection(city, source)

    pipeline = [
        {
            "$addFields": {
                "score_per_price": {
                    "$cond": [
                        {"$and": [
                            {"$isNumber": "$rating"},
                            {"$isNumber": "$price.value"},
                            {"$ne": ["$price.value", 0]}
                        ]},
                        {"$divide": ["$rating", "$price.value"]},
                        None
                    ]
                }
            }
        },
        {"$match": {"score_per_price": {"$ne": None}}},
        {
            "$group": {
                "_id": None,
                "avg_score_per_price": {"$avg": "$score_per_price"},
                "hotels": {"$push": "$$ROOT"}
            }
        },
        {"$unwind": "$hotels"},
        {
            "$addFields": {
                "hotels.quality_value_score": {
                    "$multiply": [
                        {"$divide": [
                            "$hotels.score_per_price",
                            "$avg_score_per_price"
                        ]},
                        100
                    ]
                }
            }
        },
        {"$replaceRoot": {"newRoot": "$hotels"}},
        {"$sort": {"quality_value_score": -1}},
        {"$limit": 20}
    ]

    results = list(collection.aggregate(pipeline))
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
