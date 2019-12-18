# This is the APP with Mongo and TinyDB

# Ref:
# 1. https://medium.com/@riken.mehta/full-stack-tutorial-flask-react-docker-ee316a46e876
# 2. http://radar.oreilly.com/2014/05/building-restful-apis-with-flask-in-pycharm.html
# 3. https://auth0.com/blog/using-python-flask-and-angular-to-build-modern-apps-part-1/


import datetime
import redis
import os
import json
from _datetime import datetime
from bson.objectid import ObjectId
from flask import Flask, jsonify, request, render_template
from flask_pymongo import PyMongo
from mongoManip import atsvMongoManip as at
from flask_cors import CORS
import pymongo
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt)

app = Flask(__name__)

#fills from csv
mongo_obj = at().update_mongo_from_csv()

# app.config['MONGO_DBNAME'] = 'HC_DB'
# app.config['MONGO_URI'] = 'mongodb://localhost:27017/HC_DB'
# mongo_hc_db = PyMongo(app)
# app.config['MONGO_DBNAME'] = 'log_in_register'
# app.config['MONGO_URI'] = 'mongodb://localhost:27017/log_in_register'
# app.config['JWT_SECRET_KEY'] = 'secret'
#
# mongo_user = PyMongo(app)


# connect to MongoDB with the defaults
# mongo_config = PyMongo(app, uri="mongodb://localhost:27017/config")
#
# # connect to another MongoDB database on the same host
# mongo_admin = PyMongo(app, uri="mongodb://localhost:27017/administrators")
#
# # connect to another MongoDB server altogether
# mongo_local = PyMongo(app, uri="mongodb://another.host:27017/local")
#
# # connect to another MongoDB server altogether
# mongo_test = PyMongo(app, uri="mongodb://another.host:27017/test")
#
# mongo_user = PyMongo(app, uri="mongodb://another.host:27017/mlogreg")

app.config['MONGO_DBNAME'] = 'meanloginreg'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/meanloginreg'
app.config['JWT_SECRET_KEY'] = 'secret'

mongo = PyMongo(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

CORS(app)


@app.route('/users/register', methods=['POST'])
def register():
    users = mongo.db.local
    first_name = request.get_json()['first_name']
    last_name = request.get_json()['last_name']
    email = request.get_json()['email']
    password = bcrypt.generate_password_hash(request.get_json()['password']).decode('utf-8')
    created = datetime.utcnow()

    user_id = users.insert({
        'first_name': first_name,
        'last_name': last_name,
        'email': email,
        'password': password,
        'created': created,
    })
    new_user = users.find_one({'_id': user_id})

    result = {'email': new_user['email'] + ' registered'}

    return jsonify({'result': result})


@app.route('/users/login', methods=['POST'])
def login():
    users = mongo.db.users
    email = request.get_json()['email']
    password = request.get_json()['password']
    result = ""

    response = users.find_one({'email': email})

    if response:
        if bcrypt.check_password_hash(response['password'], password):
            access_token = create_access_token(identity={
                'first_name': response['first_name'],
                'last_name': response['last_name'],
                'email': response['email']}
            )
            result = jsonify({"token": access_token})
        else:
            result = jsonify({"error": "Invalid username and password"})
    else:
        result = jsonify({"result": "No results found"})
    return result


if __name__ == '__main__':
    app.run(debug=True)

# @app.route('/api/task', methods=['GET'])
# def get_all_tasks():
#     tasks = mongo_HC_DB.db.tasks
#
#     result = []
#
#     for field in tasks.find():
#         result.append({'_id': str(field['_id']), 'Card Name': field['Card Name']})
#
#     return jsonify(result)
#
# @app.route('/api/task', methods=['POST'])
# def add_task():
#     tasks = mongo_HC_DB.db.tasks
#     card_name = request.get_json()['Card Name']
#
#     task_id = tasks.insert({'Card Name': card_name})
#     new_task = tasks.find_one({'_id': task_id})
#
#     result = {'Card Name': new_task['Card Name']}
#
#     return  jsonify({'result': result})
#
#
# @app.route('/api/task/<id>', methods=['PUT'])
# def update_task(id):
#     tasks = mongo_HC_DB.db.tasks
#     card_name = request.get_json()['Card Name']
#
#     tasks.find_one_and_update({'_id': ObjectId(id)}, {'$set': {'Card Name': card_name}}, upsert=False)
#     new_task = tasks.find_one({'_id': ObjectId(id)})
#
#     result = {'Card Name': new_task['Card Name']}
#
#     return jsonify({'result': result})
#
#
# @app.route('/api/task/<id>', methods=['DELETE'])
# def delete_task(id):
#     tasks = mongo_HC_DB.db.tasks
#
#     response = tasks.delete_one({'_id': ObjectId(id)})
#
#     if response.deleted_count == 1:
#         result = {'message': 'record deleted'}
#     else:
#         result = {'message': 'no record found'}
#
#     return jsonify({'result': result})
#
#
# @app.route("/")
# def home_page():
#     online_users = mongo_HC_DB.db.users.find({"online": True})
#     test_all_task = get_all_tasks()
#     return render_template('index.html')





#
# hockey_card_header = mongo_obj.header
# hc_db = myMongoClient[mongo_obj.db]
# collection = hc_db[mongo_obj.collection]
# @app.errorhandler(404)
# def err():
#     return jsonify({'error': 'Not found'})
#
#
# #@1 Encoder extends to support different objects, ObjectId & datetime below
# class JSONEncoder(json.JSONEncoder):
#     ''' extend json-encoder class'''
#     def default(self, o):
#         if isinstance(o, bson.objectid.ObjectId):
#             return str(o)
#         if isinstance(o, datetime.datetime):
#             return str(o)
#         return json.JSONEncoder.default(self, o)
#
#
# #@1 Creates flask obj
# app = Flask(__name__)
#
# #@1 adds mongo url to flask configuration, so connection via flask_pymongo can be made
# app.config['MONGO_URI'] = os.environ.get('DB')
# mongo = PyMongo(app)
#
# #@1 attaches modified encoder
# app.json_encoder = JSONEncoder
#
#
#
#


