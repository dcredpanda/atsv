from selenium import webdriver
import bs4 as bs
import csv
import re

import TrendScraper

# Path to geckodriver for firefox/selenium
path = r'C:\Users\micha\Downloads\geckodriver-v0.26.0-win64\geckodriver.exe'

# Get Firefox driver
driver = webdriver.Firefox(executable_path=path)



# Scraper card data from beckett
def scrape_cards(baseLink, trendDict = {}):
	driver.get(baseLink)

	html = driver.page_source

	pageSoup = bs.BeautifulSoup(html, features='html.parser')

	itemsList = pageSoup.find_all("li", class_="search-item")

	cards = []
	for item in itemsList:
		title = item.find("li", class_="title")

		if title:
			team = item.find("li", class_="team")

			attr = item.find("li", class_="attributes")
			price = item.find("div", class_="price_to_container cc_wrap tt3 tt3")

			if not price:
				price = item.find("span", class_="item-price-value")

			titleText = parse_title(title)

			playerName = parse_name(titleText)

			playerTrends = 0
			for name in playerName:
				playerTrend, trendDict = TrendScraper.get_trend(name, trendDict)
				playerTrends += playerTrend

			teamName = parse_team(team)
			teamTrend, trendDict = TrendScraper.get_trend(teamName, trendDict)
			
			rook, mem, auto, ser = parse_attr(attr)

			card = (titleText, playerName, teamName, playerTrend, teamTrend, rook, mem, auto, ser, parse_price(price))

			cards.append(card)
	return cards, trendDict

def parse_title(title):
	text = title.find_all(text=True)
	return text[1]

# Disgustingly regedit the names
def parse_name(titleText):
	reg = re.compile('#(\\w+)')
	reg = re.compile('#'+reg.search(titleText).group(1) + '(.*)')
	names = reg.search(titleText).group(1)

	reg = re.compile('[^a-zA-Z/ ]')
	names = reg.sub('', names)
	names = names.rsplit('/', 1)

	namesPerf = []
	for name in names:
		if name:
			splitWords = name.split()
			try:
				namesPerf.append(splitWords[0]+' '+splitWords[1])
			except:
				namesPerf.append(splitWords[0])

	return namesPerf

def parse_team(team):
	text = team.find_all(text=True)[2]
	reg = re.compile('[^a-zA-Z ]')
	teamName = reg.sub('', text)

	return teamName

def parse_attr(attr):
	rook = 0
	mem = 0
	auto = 0
	ser = 0

	if not attr.find("a", class_="rc hidden"): rook = 1
	if not attr.find("a", class_="mem hidden"): mem = 1
	if not attr.find("a", class_="au hidden"): auto = 1
	if not attr.find("a", class_="ser hidden"): ser = 1

	return rook,mem,auto,ser

def parse_price(price):
	valPrice = 0

	text = price.find_all(text=True)

	if len(text) > 1:
		del text[1]

	for item in text:
		num = item.replace(',', '')
		valPrice += float(num[1:])

	valPrice /= len(text)

	return valPrice

	

outFilePtr = 'card_data_Ava.csv'
saveLinkFilePtr = 'save_link.txt'


# Create list of beckett links to pull from
baseLinks = []
for i in range(1,14):
	baseLinks.append('https://marketplace.beckett.com/search_new/?sport=185225&team=Colorado+Avalanche&attr=Ser%7CRC%7CMem%7CJsy%7CAuto&condition_id=NM-MT&rowNum=250&page='+str(i))


trendDict = {}

for link in baseLinks:
	cards, trendDict = scrape_cards(link, trendDict)

	with open(outFilePtr, 'a', newline='') as outfile:
		writer = csv.writer(outfile)
		for card in cards:
			writer.writerow(card)

	with open(saveLinkFilePtr, 'w', newline='') as outfile:
		outfile.write(link)
