from sklearn import linear_model
from sklearn.preprocessing import normalize
from sklearn.model_selection import train_test_split
import sklearn.ensemble as sk

import pandas as pd
import numpy as np

import json
import TrendScraper as ts

class RegressionModel:
	# Load features, labels into model
	# Model names: Linear Regression: 'lin', Ridge Regression: 'ridge', Lasso Regression: 'lasso', Elastic Regression: 'elastic'
	def __init__(self, inputPtr = 'card_data.csv', modelName = 'lin'):
		self.xTrain, self.yTrain, self.xTest, self.yTest = self.pull_data(inputPtr)
		self.model = self.fit_model(self.xTrain, self.yTrain, modelName)

		self.csvPtr = inputPtr

	# Pulls features and labels from csv
	def pull_data(self, filePtr):
		data = pd.read_csv(filePtr, sep=',')
		data = np.array(data)

		#np.random.shuffle(data)

		x = data[...,3:14]
		y = data[...,14:]

		x = normalize(x)

		y = np.ravel(y)

		xTrain, xTest, yTrain, yTest = train_test_split(x, y, test_size=0.05)

		return xTrain, yTrain, xTest, yTest

	def change_model(self, modelName = 'lin'):
		self.model = self.fit_model(self.xTrain, self.yTrain, modelName)

	# Model names: Linear Regression: 'lin', Ridge Regression: 'ridge', boosted trees: 'boost', Elastic Regression: 'elastic'
	def fit_model(self, x, y, modelName = 'lin'):
		model = None
		if modelName == 'lin': 
			regLin = linear_model.LinearRegression()
			regLin.fit(x, y)
			model = regLin
		elif modelName == 'ridge': 
			regRidge = linear_model.Ridge()
			regRidge.fit(x, y)
			model = regRidge
		elif modelName == 'boost': 
			params = {'n_estimators': 430, 'max_depth': 5, 'min_samples_split': 2,
          'learning_rate': 0.01, 'loss': 'ls'}
			gradBoost = sk.GradientBoostingRegressor(**params)
			gradBoost.fit(x, y)
			model = gradBoost
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
	# year: year of card : integer year
	# run: run number of card : 1,0
	# patch: is patch card : 1,0
	# jsy: is jersey card : 1,0
	# stick: is sticker card : 1,0
	# rook: is rookie card : 1,0
	# mem: is memorbilia : 1,0
	# auto: is autographed : 1,0
	# ser: has serial number : 1,0
	def pred(self, name,team, year, run, patch, jsy, stick, rook, mem, auto, ser):

		trendDict = ts.get_trend_dict(self.csvPtr)

		nameTrend,trendDict = ts.get_trend(name, trendDict)
		teamTrend,trendDict = ts.get_trend(team, trendDict)

		x = np.array([nameTrend, teamTrend, year, run, patch, jsy, stick, rook, mem, auto, ser])
		x = x.reshape(1,-1)

		x = normalize(x)
		

		price = self.model.predict(x)
		return price, trendDict



def parse_json(obj):
	inputPtr = 'web_scraper/card_data_Final.csv'
	model = RegressionModel(inputPtr, 'boost')

	card = json.loads(obj)

	name = card['name']
	team = card['team']
	year = card['year']
	run = card['run']
	patch = card['patch']
	jsy = card['jsy']
	stick = card['stick']
	rook = card['rook']
	mem = card['mem']
	auto = card['auto']
	ser = card['ser']

	price, trendDict = model.pred(name,team, year, run, patch, jsy, stick, rook, mem, auto, ser)

	priceDict = {'price':price[0]}

	return json.dumps(priceDict)


def example():
	# example on what to send
	testDict = {'name':'milan hejduk',
				'team':'colorado avalanche',
				'year':2002,
				'run':10,
				'patch':0,
				'jsy':1,
				'stick':0,
				'rook':0,
				'mem':1,
				'auto':0,
				'ser':1
				}

	exampleJson = json.dumps(testDict)

	# example on how to parse return
	price = parse_json(exampleJson)
	pricejson = json.loads(price)
	print(pricejson['price'])


example()

