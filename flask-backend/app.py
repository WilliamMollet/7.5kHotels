from flask import Flask, request, jsonify
from pymongo import MongoClient
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Activer CORS pour toutes les routes

client = MongoClient("mongodb+srv://nouha:13leet37@cluster0.u3ke7.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
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


@app.route("/smart-search", methods=["GET"])
def smart_search():
    city = request.args.get("city")
    hotel_type = request.args.get("type")
    min_price = request.args.get("min_price", type=float)
    max_price = request.args.get("max_price", type=float)
    min_score = request.args.get("min_score", type=float)
    max_distance = request.args.get("max_distance", type=float)
    sort_by = request.args.get("sort_by", "rating")  # "price", "distance", etc.
    sort_order = int(request.args.get("sort_order", -1))  # -1 = DESC, 1 = ASC

    if not city:
        return jsonify({"error": "city is required"}), 400

    collection = db[city]
    pipeline = []

    match_stage = {}

    if hotel_type:
        match_stage["type"] = hotel_type
    if min_price or max_price:
        match_stage["price.value"] = {}
        if min_price:
            match_stage["price.value"]["$gte"] = min_price
        if max_price:
            match_stage["price.value"]["$lte"] = max_price
    if min_score:
        match_stage["rating.score"] = {"$gte": min_score}
    if max_distance:
        match_stage["distanceFromCenter"] = {"$lte": max_distance}

    if match_stage:
        pipeline.append({"$match": match_stage})

    # Projection pour ne retourner que les champs utiles
    pipeline.append({
        "$project": {
            "_id": 0,
            "title": 1,
            "type": 1,
            "price": 1,
            "rating": 1,
            "link": 1,
            "location": 1,
            "distanceFromCenter": 1
        }
    })

    # Tri dynamique
    sort_fields = {
        "price": "price.value",
        "rating": "rating.score",
        "distance": "distanceFromCenter"
    }
    if sort_by in sort_fields:
        pipeline.append({
            "$sort": {sort_fields[sort_by]: sort_order}
        })

    # Limit optional (e.g., top 10)
    pipeline.append({"$limit": 20})

    results = list(collection.aggregate(pipeline))
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
