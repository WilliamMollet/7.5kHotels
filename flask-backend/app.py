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

if __name__ == '__main__':
    app.run(debug=True)
