import pymongo
import datetime
import docker
import csv
import sys, getopt, pprint
import json



#Initializes mongo and creates database/collection
myMongoClient = pymongo.MongoClient('localhost', 27017)
db = myMongoClient["hc_db"]
collection = db['hc_c1']

csv_file = open("Model Stuff/web_scraper/card_data_Ava.csv", 'r')
ml_csv_reader = csv.reader(csv_file)

#USE drop below to clear collection before addition
# collection.drop()

#Turn Mongo to Object entry

hockey_card_header = ["Card Name", "Player Name", "Team Name", "N1", "N2", "N3", "N4", "N5"]

for card in ml_csv_reader:
    post_data = dict(zip(hockey_card_header, card))
    # print(post_data)
    mong_data = collection.insert_one(post_data)
    print(mong_data)
    post_data.clear()

csv_file.close()


