# This is the APP with Mongo and TinyDB

# Ref:
# 1. https://medium.com/@riken.mehta/full-stack-tutorial-flask-react-docker-ee316a46e876
# 2. http://radar.oreilly.com/2014/05/building-restful-apis-with-flask-in-pycharm.html
# 3. https://auth0.com/blog/using-python-flask-and-angular-to-build-modern-apps-part-1/


import time
import redis
import os
import json
import datetime
import bson
from flask import Flask, jsonify
from flask_pymongo import PyMongo

app = Flask(__name__)
cache = redis.Redis(host='redis', port=6379)


def get_hit_count():
    retries = 5
    while True:
        try:
            return cache.incr('hits')
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)


@app.route('/')
def hello():
    count = get_hit_count()
    return 'Hello World! I have been seen {} times.\n'.format(count)

@app.errorhandler(404)
def err():
    return jsonify({'error': 'Not found'})


#@1 Encoder extends to support different objects, ObjectId & datetime below
class JSONEncoder(json.JSONEncoder):
    ''' extend json-encoder class'''
    def default(self, o):
        if isinstance(o, bson.objectid.ObjectId):
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

if __name__ == '__main__':
    app.run()




