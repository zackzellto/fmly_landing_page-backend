from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__)
CORS(app, origins=['*'], allow_headers=['Content-Type', 'application/json'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'], supports_credentials=True)

load_dotenv()

database_url = os.environ.get('DATABASE_URL')
client = MongoClient(database_url)
fmly_waitlist_db = client.get_database('Fmly_Waitlist_DB')
waitlist_collection = fmly_waitlist_db.get_collection('collections')


@app.route('/api/waitlist', methods=['GET', 'POST'])
def waitlist_route():
    if request.method == 'GET':
        waitlist = list(waitlist_collection.find())
        # Convert ObjectId to string representation
        waitlist = [{**item, '_id': str(item['_id'])} for item in waitlist]
        return jsonify(waitlist)
    elif request.method == 'POST':
        data = request.get_json()
        result = waitlist_collection.insert_one(data)
        waitlist_item = waitlist_collection.find_one(
            {'_id': result.inserted_id})
        # Convert ObjectId to string representation
        waitlist_item['_id'] = str(waitlist_item['_id'])
        return jsonify(waitlist_item), 201


@app.route('/api/waitlist/<string:id>', methods=['GET', 'PUT', 'DELETE'])
def waitlist_item_route(id):
    waitlist_item = waitlist_collection.find_one({'_id': ObjectId(id)})
    if not waitlist_item:
        return jsonify({"error": "Not found"}), 404

    if request.method == 'GET':
        # Convert ObjectId to string representation
        waitlist_item['_id'] = str(waitlist_item['_id'])
        return jsonify(waitlist_item)
    elif request.method == 'PUT':
        data = request.get_json()
        waitlist_collection.update_one({'_id': ObjectId(id)}, {'$set': data})
        waitlist_item = waitlist_collection.find_one({'_id': ObjectId(id)})
        # Convert ObjectId to string representation
        waitlist_item['_id'] = str(waitlist_item['_id'])
        return jsonify(waitlist_item)
    elif request.method == 'DELETE':
        waitlist_collection.delete_one({'_id': ObjectId(id)})
        return jsonify({"success": True})


@app.route('/')
def index():
    return 'Hello, World!'


if __name__ == '__main__':
    app.run(debug=True)
