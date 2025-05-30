from pymongo import MongoClient
from dotenv import load_dotenv
from flask import Flask, request, jsonify


load_dotenv()
mongo_uri = os.getenv("MONGO_CLIENT")

app = Flask(__name__)

# Connexion MongoDB Atlas
client = MongoClient(mongo_uri)
db = client["ville_hotels"]

# CREATE
@app.route('/<city>/<platform>', methods=['POST'])
def create_entry(city, platform):
    data = request.json
    data["source"] = platform
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

# ADD COMMENT
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

# GET COMMENTS
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

# ADD TO FAVORITES
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

# GET FAVORITES
@app.route('/favorites', methods=['GET'])
def get_favorites():
    user = request.args.get("user")
    if not user:
        return jsonify({"error": "User is required"}), 400

    favorites = list(db["favorites"].find({"user": user}, {"_id": 0}))
    return jsonify(favorites)

# Optionnel : DELETE FAVORITE
@app.route('/favorites', methods=['DELETE'])
def delete_favorite():
    data = request.json
    user = data.get("user")
    title = data.get("title")
    result = db["favorites"].delete_one({"user": user, "title": title})
    return jsonify({"deleted": result.deleted_count})

# Lancement
if __name__ == '__main__':
    app.run(debug=True)
