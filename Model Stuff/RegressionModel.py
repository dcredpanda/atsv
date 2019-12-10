from sklearn import linear_model
from sklearn.preprocessing import normalize
import pandas as pd
import numpy as np

import json
import TrendScraper as ts

class RegressionModel:
	# Load features, labels into model
	# Model names: Linear Regression: 'lin', Ridge Regression: 'ridge', Lasso Regression: 'lasso', Elastic Regression: 'elastic'
	def __init__(self, inputPtr = 'card_data.csv', modelName = 'lin'):
		self.x, self.y = self.pull_data(inputPtr)
		self.model = self.fit_model(self.x, self.y, modelName)

		self.csvPtr = inputPtr

	# Pulls features and labels from csv
	def pull_data(self, filePtr):
		data = pd.read_csv(filePtr, sep=',',header=None)
		data = np.array(data)

		np.random.shuffle(data)

		x = data[...,4:13]
		y = data[...,13:]

		x = np.insert(x,0,1,axis=1)
		x = normalize(x)

		return x,y

	def change_model(self, modelName = 'lin'):
		self.model = self.fit_model(self.x, self.y, modelName)

	# Model names: Linear Regression: 'lin', Ridge Regression: 'ridge', Lasso Regression: 'lasso', Elastic Regression: 'elastic'
	def fit_model(self, x, y, modelName = 'lin'):
		y = np.ravel(y)

		model = None
		if modelName == 'lin': 
			regLin = linear_model.LinearRegression()
			regLin.fit(x, y)
			model = regLin
		elif modelName == 'ridge': 
			regRidge = linear_model.Ridge()
			regRidge.fit(x, y)
			model = regRidge
		elif modelName == 'lasso': 
			regLasso = linear_model.Lasso()
			regLasso.fit(x, y)
			model = regLasso
		elif modelName == 'elastic': 
			regElastic = linear_model.ElasticNetCV()
			regElastic.fit(x, y)
			model = regElastic

		return model

	# Test Data
	def test_data(self, x,y):
		print('Score: '+ str(self.model.score(x,y)))

	# Get card price prdiction
	# name: player name : string
	# team: team name : string
	# rook: is rookie card : 1,0
	# mem: is memorbilia : 1,0
	# auto: is autographed : 1,0
	# ser: has serial number : 1,0
	def pred(self, name, team, rook, mem, auto, ser):

		trendDict = ts.get_trend_dict(self.csvPtr)

		nameTrend,trendDict = ts.get_trend(name, trendDict)
		teamTrend,trendDict = ts.get_trend(team, trendDict)

		x = np.array([nameTrend, teamTrend, rook, mem, auto, ser])
		x = x.reshape(1,-1)
		x = np.insert(x,0,1,axis=1)
		x = normalize(x)

		price = self.model.predict(x)
		return price, trendDict



def parse_json(obj):
	inputPtr = 'web_scraper/card_data_All_Mod.csv'
	model = RegressionModel(inputPtr, 'ridge')

	card = json.loads(obj)

	name = card['name']
	team = card['team']
	rook = card['rook']
	mem = card['mem']
	auto = card['auto']
	ser = card['ser']

	price, trendDict = model.pred(name,team,rook, mem, auto, ser)

	priceDict = {'price':price[0]}

	return json.dumps(priceDict)


def example():
	# example on what to send
	testDict = {'name':'milan hejduk',
				'team':'colorado avalanche',
				'rook':0,
				'mem':0,
				'auto':0,
				'ser':1
				}

	exampleJson = json.dumps(testDict)

	# example on how to parse return
	price = parse_json(exampleJson)
	pricejson = json.loads(price)
	print(pricejson['price'])


inputPtr = 'web_scraper/card_data_All_Mod.csv'
model = RegressionModel(inputPtr, 'lin')


print('lin')
model.test_data(model.x, model.y)

model.change_model('ridge')
print('ridge')
model.test_data(model.x, model.y)

model.change_model('lasso')
print('lasso')
model.test_data(model.x, model.y)

model.change_model('elastic')
print('elastic')
model.test_data(model.x, model.y)