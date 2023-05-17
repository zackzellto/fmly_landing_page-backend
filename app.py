from flask import Flask, request, jsonify, abort
from datetime import datetime
from flask_swagger_ui import get_swaggerui_blueprint
from pymongo import MongoClient
from dotenv import load_dotenv, find_dotenv
from flask_cors import CORS
from datetime import datetime
import os
import uuid
from bson import ObjectId

load_dotenv(find_dotenv())

app = Flask(__name__)

CORS(app, origins=["https://fmly-landing-page-backend.herokuapp.com"])


SWAGGER_URL = '/swagger'

API_URL = '/static/swagger.json'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Fmly Landing Page API"
    }
)

DB_URL = os.environ.get("CONNECTION_STRING")

client = MongoClient(DB_URL)
databases = client.list_database_names()
fmly_waitlist_db = client['Fmly_Waitlist_DB']
collections = fmly_waitlist_db.list_collection_names()

print(collections)

email_submissions = []


def get_timestamp():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


@app.route('/api/waitlist', methods=['POST'])
def join_waitlist():
    form_data = {
        'id': str(uuid.uuid4()),
        'email': request.json['email'],
        'timestamp': get_timestamp(),
    }
    result = fmly_waitlist_db.collections.insert_one(form_data)
    if not result:
        abort(400, {'error': 'Email is required'})
    email_submissions.append(form_data)

    return jsonify({'success': True}), 201


@app.route('/api/waitlist', methods=['GET'])
def get_waitlist():
    waitlist = fmly_waitlist_db.collections.find()
    if not waitlist:
        abort(404, {'error': 'Waitlist not found'})

    waitlist_data = []
    for item in waitlist:
        item['_id'] = str(item['_id'])  # Convert ObjectId to string
        waitlist_data.append(item)

    return jsonify(waitlist_data)


@app.route('/api/waitlist/<string:id>', methods=['GET'])
def get_waitlist_by_id(id):
    waitlist = fmly_waitlist_db.collections.find_one({'id': id})
    if not waitlist:
        abort(404, {'error': 'Waitlist entry not found'})
    return jsonify(waitlist), 200


@app.route('/api/waitlist/<string:id>', methods=['PUT'])
def update_waitlist_by_id(id):
    existing_entry = fmly_waitlist_db.collections.find_one({'id': id})
    if not existing_entry:
        abort(404, {'error': 'Waitlist entry not found'})
    email = request.json.get('email')
    timestamp = get_timestamp()

    update_result = fmly_waitlist_db.collections.update_one(
        {'id': id},
        {'$set': {'email': email, 'timestamp': timestamp}}
    )
    if not update_result.modified_count:
        abort(400, {'error': 'Failed to update waitlist entry'})

    updated_entry = fmly_waitlist_db.collections.find_one({'id': id})
    return jsonify(updated_entry), 200


@app.route('/api/waitlist/<string:id>', methods=['DELETE'])
def delete_waitlist_by_id(id):
    result = fmly_waitlist_db.collections.delete_one({'id': id})
    if result.deleted_count == 0:
        abort(404, {'error': 'Waitlist entry not found'})
    elif result.deleted_count == 1:
        return jsonify({'success': True}), 200


app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)


# if __name__ == '__main__':
#     app.run(debug=True)
