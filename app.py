# This is the APP with Mongo and TinyDB

# Ref:
# 1. https://medium.com/@riken.mehta/full-stack-tutorial-flask-react-docker-ee316a46e876
# 2. http://radar.oreilly.com/2014/05/building-restful-apis-with-flask-in-pycharm.html
# 3. https://auth0.com/blog/using-python-flask-and-angular-to-build-modern-apps-part-1/


import os
import json
import datetime
from bson.objectid import ObjectId
from flask import Flask
from flask_pymongo import PyMongo


#@1 Encoder extends to support different objects, ObjectId & datetime below
class JSONEncoder(json.JSONEncoder):
    ''' extend json-encoder class'''
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime.datetime):
            return str(o)
        return json.JSONEncoder.default(self, o)


#@1 Creates flask obj
app = Flask(__name__)

#@1 adds mongo url to flask configuration, so connection via flask_pymongo can be made
app.config['MONGO_URI'] = os.environ.get('DB')
mongo = PyMongo(app)

#@1 attaches modified encoder
app.json_encoder = JSONEncoder


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()

from app.controllers import *