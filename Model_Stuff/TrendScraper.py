from pytrends.request import TrendReq
import pandas as pd
import numpy as np
import csv


# Gets a google trend value if it does not exist in trendDict
def get_trend(word, trendDict = {}):
	tot = 0

	if word not in trendDict:
		pytrends = TrendReq(hl='en-US', tz=360)
						
		kw_list = [word]

		pytrends.build_payload(kw_list, cat=260, timeframe='today 12-m', geo='US')
		data = pytrends.interest_over_time()

		if not data.empty:
			tot = data[word].sum()

		trendDict[word] = tot
	else:
		tot = trendDict[word]

	return tot, trendDict

# Load trendDict from csv
def get_trend_dict(filePtr):
	trendDict = {}

	data = pd.read_csv(filePtr, sep=',')
	data = np.array(data)

	names = data[...,1:2]
	teams = data[...,2:3]

	namesVal = data[...,3:4]
	teamsVal = data[...,4:5]
	

	for i in range(len(names)):
		if(namesVal[i] != -1) and (names[i][0].lower() not in trendDict):
			trendDict[names[i][0].lower()] = namesVal[i]

	for i in range(len(teams)):
		if(teamsVal[i] != -1) and (teams[i][0].lower() not in trendDict):
			trendDict[teams[i][0].lower()] = teamsVal[i]

	return trendDict