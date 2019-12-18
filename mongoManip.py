import pymongo
import datetime
import docker
import csv
import sys, getopt, pprint
import json


class atsvMongoManip:

    def __init__(self, csv_files=["Model Stuff/web_scraper/card_data_Ava.csv",
                              "Model Stuff/web_scraper/card_data.csv"],
                 host='localhost', port=27017, db='HC_DB', collection='HC_C1',
                 header=["Card Name", "Player Name", "Team Name", "N1", "N2", "N3", "N4", "N5"],
                 drop=False):

        self.csv_files = csv_files # TODO: refactor to subclass
        self.host = host
        self.port = port
        self.db = db
        self.collection = collection
        self.header = header
        self.drop = drop

        print(self)


    def update_mongo_from_csv(self):

        # Initializes mongo and creates database/collection
        myMongoClient = pymongo.MongoClient(self.host, self.port)
        db = myMongoClient[self.db]
        collection = db[self.collection]

        hockey_card_header = self.header

        if self.drop is True:
            # db.dropDatabase()
            collection.drop()

        for csv_file in self.csv_files:
            csv_file = open(csv_file, 'r')
            ml_csv_reader = csv.reader(csv_file)

            # USE drop below to clear collection before addition
            # collection.drop()

            # Turn Mongo to Object entry

            for card in ml_csv_reader:
                # for card in ml_csv_reader:
                post_data = dict(zip(hockey_card_header, card))
                # print(post_data)
                # mong_data = collection.insert_one(post_data)
                mongo_data = collection.update_one(post_data, {"$set": post_data}, upsert=True)

                print(mongo_data)
                post_data.clear()

            csv_file.close()
            myMongoClient.close()





# test = atsvMongoManip()
#
# test.update_mongo_from_csv()
