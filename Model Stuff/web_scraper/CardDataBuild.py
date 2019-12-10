from selenium import webdriver
import bs4 as bs
import csv
import re
import time

# Path to geckodriver for firefox/selenium
path = r'C:\Users\micha\Downloads\geckodriver-v0.26.0-win64\geckodriver.exe'

# Get Firefox driver
driver = webdriver.Firefox(executable_path=path)

# Scraper card data from beckett
def scrape_cards(baselink):
	links = scrape_links_prices(baselink)

	cards = []
	for link, tup in links:
		cards.append(scrape_cards_data(link) + tup )

	print(len(cards))
	print(cards)

	return cards

def scrape_links_prices(baseLink):
	driver.get(baseLink)

	javaScript = 'var elements = document.getElementsByClassName(\'compareItemsExpand\'); for (var i=0; i<elements.length; i++) { elements[i].click(); } return document.getElementsByTagName(\'html\')[0].innerHTML;'

	html = driver.execute_script(javaScript)

	time.sleep(30)

	html = driver.page_source
	pageSoup = bs.BeautifulSoup(html, features='html.parser')

	expandItemsList = pageSoup.find_all("li", class_="search-item multi-items showClass inner-area")

	evenItemsList = pageSoup.find_all("li", class_="search-item even")
	oddItemsList = pageSoup.find_all("li", class_="search-item odd")

	print(len(expandItemsList), len(evenItemsList), len(oddItemsList))

	links = []
	for item in expandItemsList:
		title = item.find("li", class_="title")
		if title:
			link = get_link(title)
			attr = item.find("li", class_="attributes")
			prices = item.find_all("span", class_="item-price-value")
			price = parse_price_group(prices)

			rook, mem, auto, ser = parse_attr(attr)

			links.append((link,(rook, mem, auto, ser, price)))

	for item in evenItemsList:
		title = item.find("li", class_="title")
		if title:
			link = get_link(title)
			attr = item.find("li", class_="attributes")
			price = parse_price(item.find("span", class_="item-price-value"))

			rook, mem, auto, ser = parse_attr(attr)

			links.append((link,(rook, mem, auto, ser, price)))

	for item in oddItemsList:
		title = item.find("li", class_="title")
		if title:
			link = get_link(title)
			attr = item.find("li", class_="attributes")
			price = parse_price(item.find("span", class_="item-price-value"))

			rook, mem, auto, ser = parse_attr(attr)

			links.append((link,(rook, mem, auto, ser, price)))

	print(len(links))
	return links

def scrape_cards_data(baseLink):
	driver.get(baseLink)

	html = driver.page_source

	pageSoup = bs.BeautifulSoup(html, features='html.parser')
	cardDetails = pageSoup.find("section", class_="card-details")

	title = cardDetails.find("h1", text=True).get_text()
	title = str(title).replace('\n', '')
	title = title.replace('  ', '')

	otherAttributes = cardDetails.find_all("div", class_="attributes")
	attrTuple = parse_other_attributes('')
	for item in otherAttributes:
		attr = item.find("li", text=True)
		attrTuple = parse_other_attributes(attr)

	tableText = cardDetails.find_all("li")	
	printRun = 0
	teamName = brand = playerName = year = ''

	for entry in tableText:
		strEntry = str(entry)
		if 'Print Run:' in strEntry: 
			printRun = strEntry.replace('<li>Print Run: ', '')
			printRun = printRun.replace('</li>', '')
		elif 'Team:' in strEntry: 
			teams = entry.find_all("a", text=True)
			teamName = ''
			for team in teams:
				teamName = teamName + ';' + str(team.get_text())
			teamName = teamName[1:]
		elif 'Brand:' in strEntry: 
			brand = entry.find("a", text=True).get_text()
		elif 'Player:' in strEntry: 
			players = entry.find_all("a", text=True)
			playerName = ''
			for player in players:
				playerName = playerName + ';' + str(player.get_text())
			playerName = playerName[1:]
			print(playerName)
		elif 'Year:' in strEntry: 
			year = strEntry.replace('<li>Year: ', '')
			year = year.replace('</li>', '')

	card = (title, playerName, teamName, brand, year, printRun) + attrTuple

	return card

def parse_other_attributes(attr):
	promo = patch = pads = jsy = aus = auoc = auc = stick = 0
	if attr:
		attr = attr.get_text()
		attr = attr.replace(' ', '')
		attrList = attr.split(',')

		# encode stuff
		# test all
		for item in attrList:
			if 'Promo' in item: promo = 1
			elif 'Patch' in item: patch = 1
			elif 'Pads' in item: pads = 1
			elif 'Jsy' in item: jsy = 1
			elif 'Auto Sticker' in item: aus = 1
			elif 'Auto On Card' in item: auoc = 1
			elif 'Auto Cut' in item: auc = 1
			elif 'Stick' in item: stick = 1

	return (promo, patch, pads, jsy, aus, auoc, auc, stick)


def get_link(title):
	return title.find('a')['href']

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
	num = price.find(text=True)
	num = num.replace(',', '')
	return float(num[1:])

def parse_price_group(price):
	valPrice = 0

	for item in price:
		valPrice += parse_price(item)

	valPrice /= len(price)

	return valPrice

def get_links():
	# Create list of beckett links to pull from
	baseLinks = []
	for i in range(1,20):
		baseLinks.append('https://marketplace.beckett.com/search_new/?sport=185225&condition_id=NM-MT&rowNum=250&team=Winnipeg+Jets%7CWashington+Capitals%7CVegas+Golden+Knights%7CVancouver+Canucks%7CToronto+Maple+Leafs%7CToronto+Blue+Jays%7CTeam+USA+HK%7CTeam+Canada+HK%7CTampa+Bay+Lightning%7CSt.+Louis+Blues%7CSan+Jose+Sharks%7CQuebec+Nordiques%7CPittsburgh+Steelers%7CPittsburgh+Pirates%7CPittsburgh+Penguins%7CPhoenix+Roadrunners%7CPhoenix+Coyotes%7CPhiladelphia+Flyers%7COttawa+Senators%7CNew+York+Rangers%7CNew+York+Islanders%7CNew+York+Giants+FB%7CNew+Jersey+Devils%7CNashville+Predators%7CMontreal+Canadiens%7CMinnesota+Wild%7CMinnesota+North+Stars%7CLos+Angeles+Kings%7CHouston+Aeros%7CHartford+Whalers%7CFlorida+Panthers%7CEdmonton+Oilers%7CDetroit+Red+Wings%7CDallas+Stars%7CColumbus+Blue+Jackets%7CColorado+Rockies+HK%7CColorado+Avalanche%7CCleveland+Barons%7CChicago+Blackhawks%7CCarolina+Hurricanes%7CCanada%7CCalifornia+Golden+Seals%7CCalgary+Flames%7CBuffalo+Sabres%7CBoston+Bruins%7CAtlanta+Thrashers%7CAtlanta+Flames%7CArizona+Coyotes%7CAngers+SCO%7CAnaheim+Ducks&marketplace_category_id=Cards+-+Sports&attr=Stick%7CSer%7CRC%7CPromo%7CPatch%7CPads%7CMem8%7CMem4%7CMem3%7CMem2%7CMem%7CJsy%7CAuto2%7CAuto+Sticker%7CAuto+On+Card%7CAuto+Cut%7CAuto&print_run=999%7C99%7C9500%7C950%7C949%7C94%7C900%7C90%7C899%7C89%7C875%7C850%7C85%7C849%7C83%7C825%7C800%7C80%7C799%7C780%7C775%7C750%7C75%7C74%7C70%7C699%7C6950%7C65%7C62%7C6199%7C600%7C60%7C599%7C575%7C55%7C54%7C5000%7C500%7C50%7C499%7C49%7C480%7C4750%7C45%7C4299%7C425%7C400%7C40%7C3999%7C399%7C3900%7C390%7C375%7C3500%7C350%7C35%7C349%7C3475%7C325%7C3099%7C3000%7C300%7C2999%7C299%7C290%7C275%7C2625%7C260%7C2599%7C2500%7C250%7C25%7C249%7C2400%7C225%7C2000%7C200%7C1999%7C199%7C185%7C1750%7C175%7C170%7C165%7C1500%7C150%7C15%7C1499%7C149%7C135%7C1300%7C1299%7C1250%7C125%7C1199%7C105%7C10000%7C1000%7C100%7C10&brand=Artifacts&page='+str(i))

	for i in range(7,10):
		baseLinks.append('https://marketplace.beckett.com/search_new/?sport=185225&condition_id=NM-MT&rowNum=250&team=Winnipeg+Jets%7CWashington+Capitals%7CVegas+Golden+Knights%7CVancouver+Canucks%7CToronto+Maple+Leafs%7CToronto+Blue+Jays%7CTeam+USA+HK%7CTeam+Canada+HK%7CTampa+Bay+Lightning%7CSt.+Louis+Blues%7CSan+Jose+Sharks%7CQuebec+Nordiques%7CPittsburgh+Steelers%7CPittsburgh+Pirates%7CPittsburgh+Penguins%7CPhoenix+Roadrunners%7CPhoenix+Coyotes%7CPhiladelphia+Flyers%7COttawa+Senators%7CNew+York+Rangers%7CNew+York+Islanders%7CNew+York+Giants+FB%7CNew+Jersey+Devils%7CNashville+Predators%7CMontreal+Canadiens%7CMinnesota+Wild%7CMinnesota+North+Stars%7CLos+Angeles+Kings%7CHouston+Aeros%7CHartford+Whalers%7CFlorida+Panthers%7CEdmonton+Oilers%7CDetroit+Red+Wings%7CDallas+Stars%7CColumbus+Blue+Jackets%7CColorado+Rockies+HK%7CColorado+Avalanche%7CCleveland+Barons%7CChicago+Blackhawks%7CCarolina+Hurricanes%7CCanada%7CCalifornia+Golden+Seals%7CCalgary+Flames%7CBuffalo+Sabres%7CBoston+Bruins%7CAtlanta+Thrashers%7CAtlanta+Flames%7CArizona+Coyotes%7CAngers+SCO%7CAnaheim+Ducks&marketplace_category_id=Cards+-+Sports&attr=Stick%7CSer%7CRC%7CPromo%7CPatch%7CPads%7CMem8%7CMem4%7CMem3%7CMem2%7CMem%7CJsy%7CAuto2%7CAuto+Sticker%7CAuto+On+Card%7CAuto+Cut%7CAuto&print_run=999%7C99%7C9500%7C950%7C949%7C94%7C900%7C90%7C899%7C89%7C875%7C850%7C85%7C849%7C83%7C825%7C800%7C80%7C799%7C780%7C775%7C750%7C75%7C74%7C70%7C699%7C6950%7C65%7C62%7C6199%7C600%7C60%7C599%7C575%7C55%7C54%7C5000%7C500%7C50%7C499%7C49%7C480%7C4750%7C45%7C4299%7C425%7C400%7C40%7C3999%7C399%7C3900%7C390%7C375%7C3500%7C350%7C35%7C349%7C3475%7C325%7C3099%7C3000%7C300%7C2999%7C299%7C290%7C275%7C2625%7C260%7C2599%7C2500%7C250%7C25%7C249%7C2400%7C225%7C2000%7C200%7C1999%7C199%7C185%7C1750%7C175%7C170%7C165%7C1500%7C150%7C15%7C1499%7C149%7C135%7C1300%7C1299%7C1250%7C125%7C1199%7C105%7C10000%7C1000%7C100%7C10&brand=SP+Authentic&page='+str(i))

	for i in range(1,9):
		baseLinks.append('https://marketplace.beckett.com/search_new/?sport=185225&condition_id=NM-MT&rowNum=250&team=Winnipeg+Jets%7CWashington+Capitals%7CVegas+Golden+Knights%7CVancouver+Canucks%7CToronto+Maple+Leafs%7CToronto+Blue+Jays%7CTeam+USA+HK%7CTeam+Canada+HK%7CTampa+Bay+Lightning%7CSt.+Louis+Blues%7CSan+Jose+Sharks%7CQuebec+Nordiques%7CPittsburgh+Steelers%7CPittsburgh+Pirates%7CPittsburgh+Penguins%7CPhoenix+Roadrunners%7CPhoenix+Coyotes%7CPhiladelphia+Flyers%7COttawa+Senators%7CNew+York+Rangers%7CNew+York+Islanders%7CNew+York+Giants+FB%7CNew+Jersey+Devils%7CNashville+Predators%7CMontreal+Canadiens%7CMinnesota+Wild%7CMinnesota+North+Stars%7CLos+Angeles+Kings%7CHouston+Aeros%7CHartford+Whalers%7CFlorida+Panthers%7CEdmonton+Oilers%7CDetroit+Red+Wings%7CDallas+Stars%7CColumbus+Blue+Jackets%7CColorado+Rockies+HK%7CColorado+Avalanche%7CCleveland+Barons%7CChicago+Blackhawks%7CCarolina+Hurricanes%7CCanada%7CCalifornia+Golden+Seals%7CCalgary+Flames%7CBuffalo+Sabres%7CBoston+Bruins%7CAtlanta+Thrashers%7CAtlanta+Flames%7CArizona+Coyotes%7CAngers+SCO%7CAnaheim+Ducks&marketplace_category_id=Cards+-+Sports&attr=Stick%7CSer%7CRC%7CPromo%7CPatch%7CPads%7CMem8%7CMem4%7CMem3%7CMem2%7CMem%7CJsy%7CAuto2%7CAuto+Sticker%7CAuto+On+Card%7CAuto+Cut%7CAuto&print_run=999%7C99%7C9500%7C950%7C949%7C94%7C900%7C90%7C899%7C89%7C875%7C850%7C85%7C849%7C83%7C825%7C800%7C80%7C799%7C780%7C775%7C750%7C75%7C74%7C70%7C699%7C6950%7C65%7C62%7C6199%7C600%7C60%7C599%7C575%7C55%7C54%7C5000%7C500%7C50%7C499%7C49%7C480%7C4750%7C45%7C4299%7C425%7C400%7C40%7C3999%7C399%7C3900%7C390%7C375%7C3500%7C350%7C35%7C349%7C3475%7C325%7C3099%7C3000%7C300%7C2999%7C299%7C290%7C275%7C2625%7C260%7C2599%7C2500%7C250%7C25%7C249%7C2400%7C225%7C2000%7C200%7C1999%7C199%7C185%7C1750%7C175%7C170%7C165%7C1500%7C150%7C15%7C1499%7C149%7C135%7C1300%7C1299%7C1250%7C125%7C1199%7C105%7C10000%7C1000%7C100%7C10&brand=SPx&page='+str(i))

	for i in range(1,6):
		baseLinks.append('https://marketplace.beckett.com/search_new/?sport=185225&condition_id=NM-MT&rowNum=250&team=Winnipeg+Jets|Washington+Capitals|Vegas+Golden+Knights|Vancouver+Canucks|Toronto+Maple+Leafs|Toronto+Blue+Jays|Team+USA+HK|Team+Canada+HK|Tampa+Bay+Lightning|St.+Louis+Blues|San+Jose+Sharks|Quebec+Nordiques|Pittsburgh+Steelers|Pittsburgh+Pirates|Pittsburgh+Penguins|Phoenix+Roadrunners|Phoenix+Coyotes|Philadelphia+Flyers|Ottawa+Senators|New+York+Rangers|New+York+Islanders|New+York+Giants+FB|New+Jersey+Devils|Nashville+Predators|Montreal+Canadiens|Minnesota+Wild|Minnesota+North+Stars|Los+Angeles+Kings|Houston+Aeros|Hartford+Whalers|Florida+Panthers|Edmonton+Oilers|Detroit+Red+Wings|Dallas+Stars|Columbus+Blue+Jackets|Colorado+Rockies+HK|Colorado+Avalanche|Cleveland+Barons|Chicago+Blackhawks|Carolina+Hurricanes|Canada|California+Golden+Seals|Calgary+Flames|Buffalo+Sabres|Boston+Bruins|Atlanta+Thrashers|Atlanta+Flames|Arizona+Coyotes|Angers+SCO|Anaheim+Ducks&marketplace_category_id=Cards+-+Sports&attr=Stick|Ser|RC|Promo|Patch|Pads|Mem8|Mem4|Mem3|Mem2|Mem|Jsy|Auto2|Auto+Sticker|Auto+On+Card|Auto+Cut|Auto&print_run=999|99|9500|950|949|94|900|90|899|89|875|850|85|849|83|825|800|80|799|780|775|750|75|74|70|699|6950|65|62|6199|600|60|599|575|55|54|5000|500|50|499|49|480|4750|45|4299|425|400|40|3999|399|3900|390|375|3500|350|35|349|3475|325|3099|3000|300|2999|299|290|275|2625|260|2599|2500|250|25|249|2400|225|2000|200|1999|199|185|1750|175|170|165|1500|150|15|1499|149|135|1300|1299|1250|125|1199|105|10000|1000|100|10&brand=Upper+Deck+Ice&page='+str(i))

	for i in range(7,9):
		baseLinks.append('https://marketplace.beckett.com/search_new/?sport=185225&condition_id=NM-MT&rowNum=250&team=Winnipeg+Jets%7CWashington+Capitals%7CVegas+Golden+Knights%7CVancouver+Canucks%7CToronto+Maple+Leafs%7CToronto+Blue+Jays%7CTeam+USA+HK%7CTeam+Canada+HK%7CTampa+Bay+Lightning%7CSt.+Louis+Blues%7CSan+Jose+Sharks%7CQuebec+Nordiques%7CPittsburgh+Steelers%7CPittsburgh+Pirates%7CPittsburgh+Penguins%7CPhoenix+Roadrunners%7CPhoenix+Coyotes%7CPhiladelphia+Flyers%7COttawa+Senators%7CNew+York+Rangers%7CNew+York+Islanders%7CNew+York+Giants+FB%7CNew+Jersey+Devils%7CNashville+Predators%7CMontreal+Canadiens%7CMinnesota+Wild%7CMinnesota+North+Stars%7CLos+Angeles+Kings%7CHouston+Aeros%7CHartford+Whalers%7CFlorida+Panthers%7CEdmonton+Oilers%7CDetroit+Red+Wings%7CDallas+Stars%7CColumbus+Blue+Jackets%7CColorado+Rockies+HK%7CColorado+Avalanche%7CCleveland+Barons%7CChicago+Blackhawks%7CCarolina+Hurricanes%7CCanada%7CCalifornia+Golden+Seals%7CCalgary+Flames%7CBuffalo+Sabres%7CBoston+Bruins%7CAtlanta+Thrashers%7CAtlanta+Flames%7CArizona+Coyotes%7CAngers+SCO%7CAnaheim+Ducks&marketplace_category_id=Cards+-+Sports&attr=Stick%7CSer%7CRC%7CPromo%7CPatch%7CPads%7CMem8%7CMem4%7CMem3%7CMem2%7CMem%7CJsy%7CAuto2%7CAuto+Sticker%7CAuto+On+Card%7CAuto+Cut%7CAuto&print_run=999%7C99%7C9500%7C950%7C949%7C94%7C900%7C90%7C899%7C89%7C875%7C850%7C85%7C849%7C83%7C825%7C800%7C80%7C799%7C780%7C775%7C750%7C75%7C74%7C70%7C699%7C6950%7C65%7C62%7C6199%7C600%7C60%7C599%7C575%7C55%7C54%7C5000%7C500%7C50%7C499%7C49%7C480%7C4750%7C45%7C4299%7C425%7C400%7C40%7C3999%7C399%7C3900%7C390%7C375%7C3500%7C350%7C35%7C349%7C3475%7C325%7C3099%7C3000%7C300%7C2999%7C299%7C290%7C275%7C2625%7C260%7C2599%7C2500%7C250%7C25%7C249%7C2400%7C225%7C2000%7C200%7C1999%7C199%7C185%7C1750%7C175%7C170%7C165%7C1500%7C150%7C15%7C1499%7C149%7C135%7C1300%7C1299%7C1250%7C125%7C1199%7C105%7C10000%7C1000%7C100%7C10&brand=Ultimate+Collection&page='+str(i))

	for i in range(1,14):
		baseLinks.append('https://marketplace.beckett.com/search_new/?sport=185225&condition_id=NM-MT&rowNum=250&team=Winnipeg+Jets%7CWashington+Capitals%7CVegas+Golden+Knights%7CVancouver+Canucks%7CToronto+Maple+Leafs%7CToronto+Blue+Jays%7CTeam+USA+HK%7CTeam+Canada+HK%7CTampa+Bay+Lightning%7CSt.+Louis+Blues%7CSan+Jose+Sharks%7CQuebec+Nordiques%7CPittsburgh+Steelers%7CPittsburgh+Pirates%7CPittsburgh+Penguins%7CPhoenix+Roadrunners%7CPhoenix+Coyotes%7CPhiladelphia+Flyers%7COttawa+Senators%7CNew+York+Rangers%7CNew+York+Islanders%7CNew+York+Giants+FB%7CNew+Jersey+Devils%7CNashville+Predators%7CMontreal+Canadiens%7CMinnesota+Wild%7CMinnesota+North+Stars%7CLos+Angeles+Kings%7CHouston+Aeros%7CHartford+Whalers%7CFlorida+Panthers%7CEdmonton+Oilers%7CDetroit+Red+Wings%7CDallas+Stars%7CColumbus+Blue+Jackets%7CColorado+Rockies+HK%7CColorado+Avalanche%7CCleveland+Barons%7CChicago+Blackhawks%7CCarolina+Hurricanes%7CCanada%7CCalifornia+Golden+Seals%7CCalgary+Flames%7CBuffalo+Sabres%7CBoston+Bruins%7CAtlanta+Thrashers%7CAtlanta+Flames%7CArizona+Coyotes%7CAngers+SCO%7CAnaheim+Ducks&marketplace_category_id=Cards+-+Sports&attr=Stick%7CSer%7CRC%7CPromo%7CPatch%7CPads%7CMem8%7CMem4%7CMem3%7CMem2%7CMem%7CJsy%7CAuto2%7CAuto+Sticker%7CAuto+On+Card%7CAuto+Cut%7CAuto&print_run=999%7C99%7C9500%7C950%7C949%7C94%7C900%7C90%7C899%7C89%7C875%7C850%7C85%7C849%7C83%7C825%7C800%7C80%7C799%7C780%7C775%7C750%7C75%7C74%7C70%7C699%7C6950%7C65%7C62%7C6199%7C600%7C60%7C599%7C575%7C55%7C54%7C5000%7C500%7C50%7C499%7C49%7C480%7C4750%7C45%7C4299%7C425%7C400%7C40%7C3999%7C399%7C3900%7C390%7C375%7C3500%7C350%7C35%7C349%7C3475%7C325%7C3099%7C3000%7C300%7C2999%7C299%7C290%7C275%7C2625%7C260%7C2599%7C2500%7C250%7C25%7C249%7C2400%7C225%7C2000%7C200%7C1999%7C199%7C185%7C1750%7C175%7C170%7C165%7C1500%7C150%7C15%7C1499%7C149%7C135%7C1300%7C1299%7C1250%7C125%7C1199%7C105%7C10000%7C1000%7C100%7C10&brand=O-Pee-Chee&page='+str(i))

	for i in range(1,9):
		baseLinks.append('https://marketplace.beckett.com/search_new/?sport=185225&condition_id=NM-MT&rowNum=250&team=Winnipeg+Jets%7CWashington+Capitals%7CVegas+Golden+Knights%7CVancouver+Canucks%7CToronto+Maple+Leafs%7CToronto+Blue+Jays%7CTeam+USA+HK%7CTeam+Canada+HK%7CTampa+Bay+Lightning%7CSt.+Louis+Blues%7CSan+Jose+Sharks%7CQuebec+Nordiques%7CPittsburgh+Steelers%7CPittsburgh+Pirates%7CPittsburgh+Penguins%7CPhoenix+Roadrunners%7CPhoenix+Coyotes%7CPhiladelphia+Flyers%7COttawa+Senators%7CNew+York+Rangers%7CNew+York+Islanders%7CNew+York+Giants+FB%7CNew+Jersey+Devils%7CNashville+Predators%7CMontreal+Canadiens%7CMinnesota+Wild%7CMinnesota+North+Stars%7CLos+Angeles+Kings%7CHouston+Aeros%7CHartford+Whalers%7CFlorida+Panthers%7CEdmonton+Oilers%7CDetroit+Red+Wings%7CDallas+Stars%7CColumbus+Blue+Jackets%7CColorado+Rockies+HK%7CColorado+Avalanche%7CCleveland+Barons%7CChicago+Blackhawks%7CCarolina+Hurricanes%7CCanada%7CCalifornia+Golden+Seals%7CCalgary+Flames%7CBuffalo+Sabres%7CBoston+Bruins%7CAtlanta+Thrashers%7CAtlanta+Flames%7CArizona+Coyotes%7CAngers+SCO%7CAnaheim+Ducks&marketplace_category_id=Cards+-+Sports&attr=Stick%7CSer%7CRC%7CPromo%7CPatch%7CPads%7CMem8%7CMem4%7CMem3%7CMem2%7CMem%7CJsy%7CAuto2%7CAuto+Sticker%7CAuto+On+Card%7CAuto+Cut%7CAuto&print_run=999%7C99%7C9500%7C950%7C949%7C94%7C900%7C90%7C899%7C89%7C875%7C850%7C85%7C849%7C83%7C825%7C800%7C80%7C799%7C780%7C775%7C750%7C75%7C74%7C70%7C699%7C6950%7C65%7C62%7C6199%7C600%7C60%7C599%7C575%7C55%7C54%7C5000%7C500%7C50%7C499%7C49%7C480%7C4750%7C45%7C4299%7C425%7C400%7C40%7C3999%7C399%7C3900%7C390%7C375%7C3500%7C350%7C35%7C349%7C3475%7C325%7C3099%7C3000%7C300%7C2999%7C299%7C290%7C275%7C2625%7C260%7C2599%7C2500%7C250%7C25%7C249%7C2400%7C225%7C2000%7C200%7C1999%7C199%7C185%7C1750%7C175%7C170%7C165%7C1500%7C150%7C15%7C1499%7C149%7C135%7C1300%7C1299%7C1250%7C125%7C1199%7C105%7C10000%7C1000%7C100%7C10&brand=SP+Game+Used&page='+str(i))

	for i in range(1,7):
		baseLinks.append('https://marketplace.beckett.com/search_new/?sport=185225&condition_id=NM-MT&rowNum=250&team=Winnipeg+Jets%7CWashington+Capitals%7CVegas+Golden+Knights%7CVancouver+Canucks%7CToronto+Maple+Leafs%7CToronto+Blue+Jays%7CTeam+USA+HK%7CTeam+Canada+HK%7CTampa+Bay+Lightning%7CSt.+Louis+Blues%7CSan+Jose+Sharks%7CQuebec+Nordiques%7CPittsburgh+Steelers%7CPittsburgh+Pirates%7CPittsburgh+Penguins%7CPhoenix+Roadrunners%7CPhoenix+Coyotes%7CPhiladelphia+Flyers%7COttawa+Senators%7CNew+York+Rangers%7CNew+York+Islanders%7CNew+York+Giants+FB%7CNew+Jersey+Devils%7CNashville+Predators%7CMontreal+Canadiens%7CMinnesota+Wild%7CMinnesota+North+Stars%7CLos+Angeles+Kings%7CHouston+Aeros%7CHartford+Whalers%7CFlorida+Panthers%7CEdmonton+Oilers%7CDetroit+Red+Wings%7CDallas+Stars%7CColumbus+Blue+Jackets%7CColorado+Rockies+HK%7CColorado+Avalanche%7CCleveland+Barons%7CChicago+Blackhawks%7CCarolina+Hurricanes%7CCanada%7CCalifornia+Golden+Seals%7CCalgary+Flames%7CBuffalo+Sabres%7CBoston+Bruins%7CAtlanta+Thrashers%7CAtlanta+Flames%7CArizona+Coyotes%7CAngers+SCO%7CAnaheim+Ducks&marketplace_category_id=Cards+-+Sports&attr=Stick%7CSer%7CRC%7CPromo%7CPatch%7CPads%7CMem8%7CMem4%7CMem3%7CMem2%7CMem%7CJsy%7CAuto2%7CAuto+Sticker%7CAuto+On+Card%7CAuto+Cut%7CAuto&print_run=999%7C99%7C9500%7C950%7C949%7C94%7C900%7C90%7C899%7C89%7C875%7C850%7C85%7C849%7C83%7C825%7C800%7C80%7C799%7C780%7C775%7C750%7C75%7C74%7C70%7C699%7C6950%7C65%7C62%7C6199%7C600%7C60%7C599%7C575%7C55%7C54%7C5000%7C500%7C50%7C499%7C49%7C480%7C4750%7C45%7C4299%7C425%7C400%7C40%7C3999%7C399%7C3900%7C390%7C375%7C3500%7C350%7C35%7C349%7C3475%7C325%7C3099%7C3000%7C300%7C2999%7C299%7C290%7C275%7C2625%7C260%7C2599%7C2500%7C250%7C25%7C249%7C2400%7C225%7C2000%7C200%7C1999%7C199%7C185%7C1750%7C175%7C170%7C165%7C1500%7C150%7C15%7C1499%7C149%7C135%7C1300%7C1299%7C1250%7C125%7C1199%7C105%7C10000%7C1000%7C100%7C10&brand=Upper+Deck+Trilogy&page='+str(i))

	for i in range(1,11):
		baseLinks.append('https://marketplace.beckett.com/search_new/?sport=185225&condition_id=NM-MT&rowNum=250&team=Winnipeg+Jets%7CWashington+Capitals%7CVegas+Golden+Knights%7CVancouver+Canucks%7CToronto+Maple+Leafs%7CToronto+Blue+Jays%7CTeam+USA+HK%7CTeam+Canada+HK%7CTampa+Bay+Lightning%7CSt.+Louis+Blues%7CSan+Jose+Sharks%7CQuebec+Nordiques%7CPittsburgh+Steelers%7CPittsburgh+Pirates%7CPittsburgh+Penguins%7CPhoenix+Roadrunners%7CPhoenix+Coyotes%7CPhiladelphia+Flyers%7COttawa+Senators%7CNew+York+Rangers%7CNew+York+Islanders%7CNew+York+Giants+FB%7CNew+Jersey+Devils%7CNashville+Predators%7CMontreal+Canadiens%7CMinnesota+Wild%7CMinnesota+North+Stars%7CLos+Angeles+Kings%7CHouston+Aeros%7CHartford+Whalers%7CFlorida+Panthers%7CEdmonton+Oilers%7CDetroit+Red+Wings%7CDallas+Stars%7CColumbus+Blue+Jackets%7CColorado+Rockies+HK%7CColorado+Avalanche%7CCleveland+Barons%7CChicago+Blackhawks%7CCarolina+Hurricanes%7CCanada%7CCalifornia+Golden+Seals%7CCalgary+Flames%7CBuffalo+Sabres%7CBoston+Bruins%7CAtlanta+Thrashers%7CAtlanta+Flames%7CArizona+Coyotes%7CAngers+SCO%7CAnaheim+Ducks&marketplace_category_id=Cards+-+Sports&attr=Stick%7CSer%7CRC%7CPromo%7CPatch%7CPads%7CMem8%7CMem4%7CMem3%7CMem2%7CMem%7CJsy%7CAuto2%7CAuto+Sticker%7CAuto+On+Card%7CAuto+Cut%7CAuto&print_run=999%7C99%7C9500%7C950%7C949%7C94%7C900%7C90%7C899%7C89%7C875%7C850%7C85%7C849%7C83%7C825%7C800%7C80%7C799%7C780%7C775%7C750%7C75%7C74%7C70%7C699%7C6950%7C65%7C62%7C6199%7C600%7C60%7C599%7C575%7C55%7C54%7C5000%7C500%7C50%7C499%7C49%7C480%7C4750%7C45%7C4299%7C425%7C400%7C40%7C3999%7C399%7C3900%7C390%7C375%7C3500%7C350%7C35%7C349%7C3475%7C325%7C3099%7C3000%7C300%7C2999%7C299%7C290%7C275%7C2625%7C260%7C2599%7C2500%7C250%7C25%7C249%7C2400%7C225%7C2000%7C200%7C1999%7C199%7C185%7C1750%7C175%7C170%7C165%7C1500%7C150%7C15%7C1499%7C149%7C135%7C1300%7C1299%7C1250%7C125%7C1199%7C105%7C10000%7C1000%7C100%7C10&brand=Pacific&page='+str(i))

	for i in range(1,8):
		baseLinks.append('https://marketplace.beckett.com/search_new/?sport=185225&condition_id=NM-MT&rowNum=250&team=Winnipeg+Jets%7CWashington+Capitals%7CVegas+Golden+Knights%7CVancouver+Canucks%7CToronto+Maple+Leafs%7CToronto+Blue+Jays%7CTeam+USA+HK%7CTeam+Canada+HK%7CTampa+Bay+Lightning%7CSt.+Louis+Blues%7CSan+Jose+Sharks%7CQuebec+Nordiques%7CPittsburgh+Steelers%7CPittsburgh+Pirates%7CPittsburgh+Penguins%7CPhoenix+Roadrunners%7CPhoenix+Coyotes%7CPhiladelphia+Flyers%7COttawa+Senators%7CNew+York+Rangers%7CNew+York+Islanders%7CNew+York+Giants+FB%7CNew+Jersey+Devils%7CNashville+Predators%7CMontreal+Canadiens%7CMinnesota+Wild%7CMinnesota+North+Stars%7CLos+Angeles+Kings%7CHouston+Aeros%7CHartford+Whalers%7CFlorida+Panthers%7CEdmonton+Oilers%7CDetroit+Red+Wings%7CDallas+Stars%7CColumbus+Blue+Jackets%7CColorado+Rockies+HK%7CColorado+Avalanche%7CCleveland+Barons%7CChicago+Blackhawks%7CCarolina+Hurricanes%7CCanada%7CCalifornia+Golden+Seals%7CCalgary+Flames%7CBuffalo+Sabres%7CBoston+Bruins%7CAtlanta+Thrashers%7CAtlanta+Flames%7CArizona+Coyotes%7CAngers+SCO%7CAnaheim+Ducks&marketplace_category_id=Cards+-+Sports&attr=Stick%7CSer%7CRC%7CPromo%7CPatch%7CPads%7CMem8%7CMem4%7CMem3%7CMem2%7CMem%7CJsy%7CAuto2%7CAuto+Sticker%7CAuto+On+Card%7CAuto+Cut%7CAuto&print_run=999%7C99%7C9500%7C950%7C949%7C94%7C900%7C90%7C899%7C89%7C875%7C850%7C85%7C849%7C83%7C825%7C800%7C80%7C799%7C780%7C775%7C750%7C75%7C74%7C70%7C699%7C6950%7C65%7C62%7C6199%7C600%7C60%7C599%7C575%7C55%7C54%7C5000%7C500%7C50%7C499%7C49%7C480%7C4750%7C45%7C4299%7C425%7C400%7C40%7C3999%7C399%7C3900%7C390%7C375%7C3500%7C350%7C35%7C349%7C3475%7C325%7C3099%7C3000%7C300%7C2999%7C299%7C290%7C275%7C2625%7C260%7C2599%7C2500%7C250%7C25%7C249%7C2400%7C225%7C2000%7C200%7C1999%7C199%7C185%7C1750%7C175%7C170%7C165%7C1500%7C150%7C15%7C1499%7C149%7C135%7C1300%7C1299%7C1250%7C125%7C1199%7C105%7C10000%7C1000%7C100%7C10&brand=Limited&page='+str(i))

	for i in range(1,8):
		baseLinks.append('https://marketplace.beckett.com/search_new/?sport=185225&condition_id=NM-MT&rowNum=250&team=Winnipeg+Jets%7CWashington+Capitals%7CVegas+Golden+Knights%7CVancouver+Canucks%7CToronto+Maple+Leafs%7CToronto+Blue+Jays%7CTeam+USA+HK%7CTeam+Canada+HK%7CTampa+Bay+Lightning%7CSt.+Louis+Blues%7CSan+Jose+Sharks%7CQuebec+Nordiques%7CPittsburgh+Steelers%7CPittsburgh+Pirates%7CPittsburgh+Penguins%7CPhoenix+Roadrunners%7CPhoenix+Coyotes%7CPhiladelphia+Flyers%7COttawa+Senators%7CNew+York+Rangers%7CNew+York+Islanders%7CNew+York+Giants+FB%7CNew+Jersey+Devils%7CNashville+Predators%7CMontreal+Canadiens%7CMinnesota+Wild%7CMinnesota+North+Stars%7CLos+Angeles+Kings%7CHouston+Aeros%7CHartford+Whalers%7CFlorida+Panthers%7CEdmonton+Oilers%7CDetroit+Red+Wings%7CDallas+Stars%7CColumbus+Blue+Jackets%7CColorado+Rockies+HK%7CColorado+Avalanche%7CCleveland+Barons%7CChicago+Blackhawks%7CCarolina+Hurricanes%7CCanada%7CCalifornia+Golden+Seals%7CCalgary+Flames%7CBuffalo+Sabres%7CBoston+Bruins%7CAtlanta+Thrashers%7CAtlanta+Flames%7CArizona+Coyotes%7CAngers+SCO%7CAnaheim+Ducks&marketplace_category_id=Cards+-+Sports&attr=Stick%7CSer%7CRC%7CPromo%7CPatch%7CPads%7CMem8%7CMem4%7CMem3%7CMem2%7CMem%7CJsy%7CAuto2%7CAuto+Sticker%7CAuto+On+Card%7CAuto+Cut%7CAuto&print_run=999%7C99%7C9500%7C950%7C949%7C94%7C900%7C90%7C899%7C89%7C875%7C850%7C85%7C849%7C83%7C825%7C800%7C80%7C799%7C780%7C775%7C750%7C75%7C74%7C70%7C699%7C6950%7C65%7C62%7C6199%7C600%7C60%7C599%7C575%7C55%7C54%7C5000%7C500%7C50%7C499%7C49%7C480%7C4750%7C45%7C4299%7C425%7C400%7C40%7C3999%7C399%7C3900%7C390%7C375%7C3500%7C350%7C35%7C349%7C3475%7C325%7C3099%7C3000%7C300%7C2999%7C299%7C290%7C275%7C2625%7C260%7C2599%7C2500%7C250%7C25%7C249%7C2400%7C225%7C2000%7C200%7C1999%7C199%7C185%7C1750%7C175%7C170%7C165%7C1500%7C150%7C15%7C1499%7C149%7C135%7C1300%7C1299%7C1250%7C125%7C1199%7C105%7C10000%7C1000%7C100%7C10&brand=BAP+Memorabilia&page='+str(i))

	for i in range(1,3):
		baseLinks.append('https://marketplace.beckett.com/search_new/?sport=185225&condition_id=NM-MT&rowNum=250&team=Winnipeg+Jets%7CWashington+Capitals%7CVegas+Golden+Knights%7CVancouver+Canucks%7CToronto+Maple+Leafs%7CToronto+Blue+Jays%7CTeam+USA+HK%7CTeam+Canada+HK%7CTampa+Bay+Lightning%7CSt.+Louis+Blues%7CSan+Jose+Sharks%7CQuebec+Nordiques%7CPittsburgh+Steelers%7CPittsburgh+Pirates%7CPittsburgh+Penguins%7CPhoenix+Roadrunners%7CPhoenix+Coyotes%7CPhiladelphia+Flyers%7COttawa+Senators%7CNew+York+Rangers%7CNew+York+Islanders%7CNew+York+Giants+FB%7CNew+Jersey+Devils%7CNashville+Predators%7CMontreal+Canadiens%7CMinnesota+Wild%7CMinnesota+North+Stars%7CLos+Angeles+Kings%7CHouston+Aeros%7CHartford+Whalers%7CFlorida+Panthers%7CEdmonton+Oilers%7CDetroit+Red+Wings%7CDallas+Stars%7CColumbus+Blue+Jackets%7CColorado+Rockies+HK%7CColorado+Avalanche%7CCleveland+Barons%7CChicago+Blackhawks%7CCarolina+Hurricanes%7CCanada%7CCalifornia+Golden+Seals%7CCalgary+Flames%7CBuffalo+Sabres%7CBoston+Bruins%7CAtlanta+Thrashers%7CAtlanta+Flames%7CArizona+Coyotes%7CAngers+SCO%7CAnaheim+Ducks&marketplace_category_id=Cards+-+Sports&attr=Stick%7CSer%7CRC%7CPromo%7CPatch%7CPads%7CMem8%7CMem4%7CMem3%7CMem2%7CMem%7CJsy%7CAuto2%7CAuto+Sticker%7CAuto+On+Card%7CAuto+Cut%7CAuto&print_run=999%7C99%7C9500%7C950%7C949%7C94%7C900%7C90%7C899%7C89%7C875%7C850%7C85%7C849%7C83%7C825%7C800%7C80%7C799%7C780%7C775%7C750%7C75%7C74%7C70%7C699%7C6950%7C65%7C62%7C6199%7C600%7C60%7C599%7C575%7C55%7C54%7C5000%7C500%7C50%7C499%7C49%7C480%7C4750%7C45%7C4299%7C425%7C400%7C40%7C3999%7C399%7C3900%7C390%7C375%7C3500%7C350%7C35%7C349%7C3475%7C325%7C3099%7C3000%7C300%7C2999%7C299%7C290%7C275%7C2625%7C260%7C2599%7C2500%7C250%7C25%7C249%7C2400%7C225%7C2000%7C200%7C1999%7C199%7C185%7C1750%7C175%7C170%7C165%7C1500%7C150%7C15%7C1499%7C149%7C135%7C1300%7C1299%7C1250%7C125%7C1199%7C105%7C10000%7C1000%7C100%7C10&brand=SPx+Finite&page='+str(i))

	for i in range(1,9):
		baseLinks.append('https://marketplace.beckett.com/search_new/?sport=185225&condition_id=NM-MT&rowNum=250&team=Winnipeg+Jets%7CWashington+Capitals%7CVegas+Golden+Knights%7CVancouver+Canucks%7CToronto+Maple+Leafs%7CToronto+Blue+Jays%7CTeam+USA+HK%7CTeam+Canada+HK%7CTampa+Bay+Lightning%7CSt.+Louis+Blues%7CSan+Jose+Sharks%7CQuebec+Nordiques%7CPittsburgh+Steelers%7CPittsburgh+Pirates%7CPittsburgh+Penguins%7CPhoenix+Roadrunners%7CPhoenix+Coyotes%7CPhiladelphia+Flyers%7COttawa+Senators%7CNew+York+Rangers%7CNew+York+Islanders%7CNew+York+Giants+FB%7CNew+Jersey+Devils%7CNashville+Predators%7CMontreal+Canadiens%7CMinnesota+Wild%7CMinnesota+North+Stars%7CLos+Angeles+Kings%7CHouston+Aeros%7CHartford+Whalers%7CFlorida+Panthers%7CEdmonton+Oilers%7CDetroit+Red+Wings%7CDallas+Stars%7CColumbus+Blue+Jackets%7CColorado+Rockies+HK%7CColorado+Avalanche%7CCleveland+Barons%7CChicago+Blackhawks%7CCarolina+Hurricanes%7CCanada%7CCalifornia+Golden+Seals%7CCalgary+Flames%7CBuffalo+Sabres%7CBoston+Bruins%7CAtlanta+Thrashers%7CAtlanta+Flames%7CArizona+Coyotes%7CAngers+SCO%7CAnaheim+Ducks&marketplace_category_id=Cards+-+Sports&attr=Stick%7CSer%7CRC%7CPromo%7CPatch%7CPads%7CMem8%7CMem4%7CMem3%7CMem2%7CMem%7CJsy%7CAuto2%7CAuto+Sticker%7CAuto+On+Card%7CAuto+Cut%7CAuto&print_run=999%7C99%7C9500%7C950%7C949%7C94%7C900%7C90%7C899%7C89%7C875%7C850%7C85%7C849%7C83%7C825%7C800%7C80%7C799%7C780%7C775%7C750%7C75%7C74%7C70%7C699%7C6950%7C65%7C62%7C6199%7C600%7C60%7C599%7C575%7C55%7C54%7C5000%7C500%7C50%7C499%7C49%7C480%7C4750%7C45%7C4299%7C425%7C400%7C40%7C3999%7C399%7C3900%7C390%7C375%7C3500%7C350%7C35%7C349%7C3475%7C325%7C3099%7C3000%7C300%7C2999%7C299%7C290%7C275%7C2625%7C260%7C2599%7C2500%7C250%7C25%7C249%7C2400%7C225%7C2000%7C200%7C1999%7C199%7C185%7C1750%7C175%7C170%7C165%7C1500%7C150%7C15%7C1499%7C149%7C135%7C1300%7C1299%7C1250%7C125%7C1199%7C105%7C10000%7C1000%7C100%7C10&brand=Upper+Deck&page='+str(i))

	for i in range(1,3):
		baseLinks.append('https://marketplace.beckett.com/search_new/?sport=185225&condition_id=NM-MT&rowNum=250&team=Winnipeg+Jets%7CWashington+Capitals%7CVegas+Golden+Knights%7CVancouver+Canucks%7CToronto+Maple+Leafs%7CToronto+Blue+Jays%7CTeam+USA+HK%7CTeam+Canada+HK%7CTampa+Bay+Lightning%7CSt.+Louis+Blues%7CSan+Jose+Sharks%7CQuebec+Nordiques%7CPittsburgh+Steelers%7CPittsburgh+Pirates%7CPittsburgh+Penguins%7CPhoenix+Roadrunners%7CPhoenix+Coyotes%7CPhiladelphia+Flyers%7COttawa+Senators%7CNew+York+Rangers%7CNew+York+Islanders%7CNew+York+Giants+FB%7CNew+Jersey+Devils%7CNashville+Predators%7CMontreal+Canadiens%7CMinnesota+Wild%7CMinnesota+North+Stars%7CLos+Angeles+Kings%7CHouston+Aeros%7CHartford+Whalers%7CFlorida+Panthers%7CEdmonton+Oilers%7CDetroit+Red+Wings%7CDallas+Stars%7CColumbus+Blue+Jackets%7CColorado+Rockies+HK%7CColorado+Avalanche%7CCleveland+Barons%7CChicago+Blackhawks%7CCarolina+Hurricanes%7CCanada%7CCalifornia+Golden+Seals%7CCalgary+Flames%7CBuffalo+Sabres%7CBoston+Bruins%7CAtlanta+Thrashers%7CAtlanta+Flames%7CArizona+Coyotes%7CAngers+SCO%7CAnaheim+Ducks&marketplace_category_id=Cards+-+Sports&attr=Stick%7CSer%7CRC%7CPromo%7CPatch%7CPads%7CMem8%7CMem4%7CMem3%7CMem2%7CMem%7CJsy%7CAuto2%7CAuto+Sticker%7CAuto+On+Card%7CAuto+Cut%7CAuto&print_run=999%7C99%7C9500%7C950%7C949%7C94%7C900%7C90%7C899%7C89%7C875%7C850%7C85%7C849%7C83%7C825%7C800%7C80%7C799%7C780%7C775%7C750%7C75%7C74%7C70%7C699%7C6950%7C65%7C62%7C6199%7C600%7C60%7C599%7C575%7C55%7C54%7C5000%7C500%7C50%7C499%7C49%7C480%7C4750%7C45%7C4299%7C425%7C400%7C40%7C3999%7C399%7C3900%7C390%7C375%7C3500%7C350%7C35%7C349%7C3475%7C325%7C3099%7C3000%7C300%7C2999%7C299%7C290%7C275%7C2625%7C260%7C2599%7C2500%7C250%7C25%7C249%7C2400%7C225%7C2000%7C200%7C1999%7C199%7C185%7C1750%7C175%7C170%7C165%7C1500%7C150%7C15%7C1499%7C149%7C135%7C1300%7C1299%7C1250%7C125%7C1199%7C105%7C10000%7C1000%7C100%7C10&brand=Pinnacle+Totally+Certified&page='+str(i))

	for i in range(1,4):
		baseLinks.append('https://marketplace.beckett.com/search_new/?sport=185225&condition_id=NM-MT&rowNum=250&team=Winnipeg+Jets%7CWashington+Capitals%7CVegas+Golden+Knights%7CVancouver+Canucks%7CToronto+Maple+Leafs%7CToronto+Blue+Jays%7CTeam+USA+HK%7CTeam+Canada+HK%7CTampa+Bay+Lightning%7CSt.+Louis+Blues%7CSan+Jose+Sharks%7CQuebec+Nordiques%7CPittsburgh+Steelers%7CPittsburgh+Pirates%7CPittsburgh+Penguins%7CPhoenix+Roadrunners%7CPhoenix+Coyotes%7CPhiladelphia+Flyers%7COttawa+Senators%7CNew+York+Rangers%7CNew+York+Islanders%7CNew+York+Giants+FB%7CNew+Jersey+Devils%7CNashville+Predators%7CMontreal+Canadiens%7CMinnesota+Wild%7CMinnesota+North+Stars%7CLos+Angeles+Kings%7CHouston+Aeros%7CHartford+Whalers%7CFlorida+Panthers%7CEdmonton+Oilers%7CDetroit+Red+Wings%7CDallas+Stars%7CColumbus+Blue+Jackets%7CColorado+Rockies+HK%7CColorado+Avalanche%7CCleveland+Barons%7CChicago+Blackhawks%7CCarolina+Hurricanes%7CCanada%7CCalifornia+Golden+Seals%7CCalgary+Flames%7CBuffalo+Sabres%7CBoston+Bruins%7CAtlanta+Thrashers%7CAtlanta+Flames%7CArizona+Coyotes%7CAngers+SCO%7CAnaheim+Ducks&marketplace_category_id=Cards+-+Sports&attr=Stick%7CSer%7CRC%7CPromo%7CPatch%7CPads%7CMem8%7CMem4%7CMem3%7CMem2%7CMem%7CJsy%7CAuto2%7CAuto+Sticker%7CAuto+On+Card%7CAuto+Cut%7CAuto&print_run=999%7C99%7C9500%7C950%7C949%7C94%7C900%7C90%7C899%7C89%7C875%7C850%7C85%7C849%7C83%7C825%7C800%7C80%7C799%7C780%7C775%7C750%7C75%7C74%7C70%7C699%7C6950%7C65%7C62%7C6199%7C600%7C60%7C599%7C575%7C55%7C54%7C5000%7C500%7C50%7C499%7C49%7C480%7C4750%7C45%7C4299%7C425%7C400%7C40%7C3999%7C399%7C3900%7C390%7C375%7C3500%7C350%7C35%7C349%7C3475%7C325%7C3099%7C3000%7C300%7C2999%7C299%7C290%7C275%7C2625%7C260%7C2599%7C2500%7C250%7C25%7C249%7C2400%7C225%7C2000%7C200%7C1999%7C199%7C185%7C1750%7C175%7C170%7C165%7C1500%7C150%7C15%7C1499%7C149%7C135%7C1300%7C1299%7C1250%7C125%7C1199%7C105%7C10000%7C1000%7C100%7C10&brand=Panini+Contenders&page='+str(i))

	for i in range(1,5):
		baseLinks.append('https://marketplace.beckett.com/search_new/?sport=185225&condition_id=NM-MT&rowNum=250&team=Winnipeg+Jets%7CWashington+Capitals%7CVegas+Golden+Knights%7CVancouver+Canucks%7CToronto+Maple+Leafs%7CToronto+Blue+Jays%7CTeam+USA+HK%7CTeam+Canada+HK%7CTampa+Bay+Lightning%7CSt.+Louis+Blues%7CSan+Jose+Sharks%7CQuebec+Nordiques%7CPittsburgh+Steelers%7CPittsburgh+Pirates%7CPittsburgh+Penguins%7CPhoenix+Roadrunners%7CPhoenix+Coyotes%7CPhiladelphia+Flyers%7COttawa+Senators%7CNew+York+Rangers%7CNew+York+Islanders%7CNew+York+Giants+FB%7CNew+Jersey+Devils%7CNashville+Predators%7CMontreal+Canadiens%7CMinnesota+Wild%7CMinnesota+North+Stars%7CLos+Angeles+Kings%7CHouston+Aeros%7CHartford+Whalers%7CFlorida+Panthers%7CEdmonton+Oilers%7CDetroit+Red+Wings%7CDallas+Stars%7CColumbus+Blue+Jackets%7CColorado+Rockies+HK%7CColorado+Avalanche%7CCleveland+Barons%7CChicago+Blackhawks%7CCarolina+Hurricanes%7CCanada%7CCalifornia+Golden+Seals%7CCalgary+Flames%7CBuffalo+Sabres%7CBoston+Bruins%7CAtlanta+Thrashers%7CAtlanta+Flames%7CArizona+Coyotes%7CAngers+SCO%7CAnaheim+Ducks&marketplace_category_id=Cards+-+Sports&attr=Stick%7CSer%7CRC%7CPromo%7CPatch%7CPads%7CMem8%7CMem4%7CMem3%7CMem2%7CMem%7CJsy%7CAuto2%7CAuto+Sticker%7CAuto+On+Card%7CAuto+Cut%7CAuto&print_run=999%7C99%7C9500%7C950%7C949%7C94%7C900%7C90%7C899%7C89%7C875%7C850%7C85%7C849%7C83%7C825%7C800%7C80%7C799%7C780%7C775%7C750%7C75%7C74%7C70%7C699%7C6950%7C65%7C62%7C6199%7C600%7C60%7C599%7C575%7C55%7C54%7C5000%7C500%7C50%7C499%7C49%7C480%7C4750%7C45%7C4299%7C425%7C400%7C40%7C3999%7C399%7C3900%7C390%7C375%7C3500%7C350%7C35%7C349%7C3475%7C325%7C3099%7C3000%7C300%7C2999%7C299%7C290%7C275%7C2625%7C260%7C2599%7C2500%7C250%7C25%7C249%7C2400%7C225%7C2000%7C200%7C1999%7C199%7C185%7C1750%7C175%7C170%7C165%7C1500%7C150%7C15%7C1499%7C149%7C135%7C1300%7C1299%7C1250%7C125%7C1199%7C105%7C10000%7C1000%7C100%7C10&brand=Panini+Prime&page='+str(i))

	for i in range(1,4):
		baseLinks.append('https://marketplace.beckett.com/search_new/?sport=185225&condition_id=NM-MT&rowNum=250&team=Winnipeg+Jets%7CWashington+Capitals%7CVegas+Golden+Knights%7CVancouver+Canucks%7CToronto+Maple+Leafs%7CToronto+Blue+Jays%7CTeam+USA+HK%7CTeam+Canada+HK%7CTampa+Bay+Lightning%7CSt.+Louis+Blues%7CSan+Jose+Sharks%7CQuebec+Nordiques%7CPittsburgh+Steelers%7CPittsburgh+Pirates%7CPittsburgh+Penguins%7CPhoenix+Roadrunners%7CPhoenix+Coyotes%7CPhiladelphia+Flyers%7COttawa+Senators%7CNew+York+Rangers%7CNew+York+Islanders%7CNew+York+Giants+FB%7CNew+Jersey+Devils%7CNashville+Predators%7CMontreal+Canadiens%7CMinnesota+Wild%7CMinnesota+North+Stars%7CLos+Angeles+Kings%7CHouston+Aeros%7CHartford+Whalers%7CFlorida+Panthers%7CEdmonton+Oilers%7CDetroit+Red+Wings%7CDallas+Stars%7CColumbus+Blue+Jackets%7CColorado+Rockies+HK%7CColorado+Avalanche%7CCleveland+Barons%7CChicago+Blackhawks%7CCarolina+Hurricanes%7CCanada%7CCalifornia+Golden+Seals%7CCalgary+Flames%7CBuffalo+Sabres%7CBoston+Bruins%7CAtlanta+Thrashers%7CAtlanta+Flames%7CArizona+Coyotes%7CAngers+SCO%7CAnaheim+Ducks&marketplace_category_id=Cards+-+Sports&attr=Stick%7CSer%7CRC%7CPromo%7CPatch%7CPads%7CMem8%7CMem4%7CMem3%7CMem2%7CMem%7CJsy%7CAuto2%7CAuto+Sticker%7CAuto+On+Card%7CAuto+Cut%7CAuto&print_run=999%7C99%7C9500%7C950%7C949%7C94%7C900%7C90%7C899%7C89%7C875%7C850%7C85%7C849%7C83%7C825%7C800%7C80%7C799%7C780%7C775%7C750%7C75%7C74%7C70%7C699%7C6950%7C65%7C62%7C6199%7C600%7C60%7C599%7C575%7C55%7C54%7C5000%7C500%7C50%7C499%7C49%7C480%7C4750%7C45%7C4299%7C425%7C400%7C40%7C3999%7C399%7C3900%7C390%7C375%7C3500%7C350%7C35%7C349%7C3475%7C325%7C3099%7C3000%7C300%7C2999%7C299%7C290%7C275%7C2625%7C260%7C2599%7C2500%7C250%7C25%7C249%7C2400%7C225%7C2000%7C200%7C1999%7C199%7C185%7C1750%7C175%7C170%7C165%7C1500%7C150%7C15%7C1499%7C149%7C135%7C1300%7C1299%7C1250%7C125%7C1199%7C105%7C10000%7C1000%7C100%7C10&brand=Parkhurst&page='+str(i))

	for i in range(1,5):
		baseLinks.append('https://marketplace.beckett.com/search_new/?sport=185225&condition_id=NM-MT&rowNum=250&team=Winnipeg+Jets%7CWashington+Capitals%7CVegas+Golden+Knights%7CVancouver+Canucks%7CToronto+Maple+Leafs%7CToronto+Blue+Jays%7CTeam+USA+HK%7CTeam+Canada+HK%7CTampa+Bay+Lightning%7CSt.+Louis+Blues%7CSan+Jose+Sharks%7CQuebec+Nordiques%7CPittsburgh+Steelers%7CPittsburgh+Pirates%7CPittsburgh+Penguins%7CPhoenix+Roadrunners%7CPhoenix+Coyotes%7CPhiladelphia+Flyers%7COttawa+Senators%7CNew+York+Rangers%7CNew+York+Islanders%7CNew+York+Giants+FB%7CNew+Jersey+Devils%7CNashville+Predators%7CMontreal+Canadiens%7CMinnesota+Wild%7CMinnesota+North+Stars%7CLos+Angeles+Kings%7CHouston+Aeros%7CHartford+Whalers%7CFlorida+Panthers%7CEdmonton+Oilers%7CDetroit+Red+Wings%7CDallas+Stars%7CColumbus+Blue+Jackets%7CColorado+Rockies+HK%7CColorado+Avalanche%7CCleveland+Barons%7CChicago+Blackhawks%7CCarolina+Hurricanes%7CCanada%7CCalifornia+Golden+Seals%7CCalgary+Flames%7CBuffalo+Sabres%7CBoston+Bruins%7CAtlanta+Thrashers%7CAtlanta+Flames%7CArizona+Coyotes%7CAngers+SCO%7CAnaheim+Ducks&marketplace_category_id=Cards+-+Sports&attr=Stick%7CSer%7CRC%7CPromo%7CPatch%7CPads%7CMem8%7CMem4%7CMem3%7CMem2%7CMem%7CJsy%7CAuto2%7CAuto+Sticker%7CAuto+On+Card%7CAuto+Cut%7CAuto&print_run=999%7C99%7C9500%7C950%7C949%7C94%7C900%7C90%7C899%7C89%7C875%7C850%7C85%7C849%7C83%7C825%7C800%7C80%7C799%7C780%7C775%7C750%7C75%7C74%7C70%7C699%7C6950%7C65%7C62%7C6199%7C600%7C60%7C599%7C575%7C55%7C54%7C5000%7C500%7C50%7C499%7C49%7C480%7C4750%7C45%7C4299%7C425%7C400%7C40%7C3999%7C399%7C3900%7C390%7C375%7C3500%7C350%7C35%7C349%7C3475%7C325%7C3099%7C3000%7C300%7C2999%7C299%7C290%7C275%7C2625%7C260%7C2599%7C2500%7C250%7C25%7C249%7C2400%7C225%7C2000%7C200%7C1999%7C199%7C185%7C1750%7C175%7C170%7C165%7C1500%7C150%7C15%7C1499%7C149%7C135%7C1300%7C1299%7C1250%7C125%7C1199%7C105%7C10000%7C1000%7C100%7C10&brand=Certified&page='+str(i))

	for i in range(1,5):
		baseLinks.append('https://marketplace.beckett.com/search_new/?sport=185225&condition_id=NM-MT&rowNum=250&team=Winnipeg+Jets%7CWashington+Capitals%7CVegas+Golden+Knights%7CVancouver+Canucks%7CToronto+Maple+Leafs%7CToronto+Blue+Jays%7CTeam+USA+HK%7CTeam+Canada+HK%7CTampa+Bay+Lightning%7CSt.+Louis+Blues%7CSan+Jose+Sharks%7CQuebec+Nordiques%7CPittsburgh+Steelers%7CPittsburgh+Pirates%7CPittsburgh+Penguins%7CPhoenix+Roadrunners%7CPhoenix+Coyotes%7CPhiladelphia+Flyers%7COttawa+Senators%7CNew+York+Rangers%7CNew+York+Islanders%7CNew+York+Giants+FB%7CNew+Jersey+Devils%7CNashville+Predators%7CMontreal+Canadiens%7CMinnesota+Wild%7CMinnesota+North+Stars%7CLos+Angeles+Kings%7CHouston+Aeros%7CHartford+Whalers%7CFlorida+Panthers%7CEdmonton+Oilers%7CDetroit+Red+Wings%7CDallas+Stars%7CColumbus+Blue+Jackets%7CColorado+Rockies+HK%7CColorado+Avalanche%7CCleveland+Barons%7CChicago+Blackhawks%7CCarolina+Hurricanes%7CCanada%7CCalifornia+Golden+Seals%7CCalgary+Flames%7CBuffalo+Sabres%7CBoston+Bruins%7CAtlanta+Thrashers%7CAtlanta+Flames%7CArizona+Coyotes%7CAngers+SCO%7CAnaheim+Ducks&marketplace_category_id=Cards+-+Sports&attr=Stick%7CSer%7CRC%7CPromo%7CPatch%7CPads%7CMem8%7CMem4%7CMem3%7CMem2%7CMem%7CJsy%7CAuto2%7CAuto+Sticker%7CAuto+On+Card%7CAuto+Cut%7CAuto&print_run=999%7C99%7C9500%7C950%7C949%7C94%7C900%7C90%7C899%7C89%7C875%7C850%7C85%7C849%7C83%7C825%7C800%7C80%7C799%7C780%7C775%7C750%7C75%7C74%7C70%7C699%7C6950%7C65%7C62%7C6199%7C600%7C60%7C599%7C575%7C55%7C54%7C5000%7C500%7C50%7C499%7C49%7C480%7C4750%7C45%7C4299%7C425%7C400%7C40%7C3999%7C399%7C3900%7C390%7C375%7C3500%7C350%7C35%7C349%7C3475%7C325%7C3099%7C3000%7C300%7C2999%7C299%7C290%7C275%7C2625%7C260%7C2599%7C2500%7C250%7C25%7C249%7C2400%7C225%7C2000%7C200%7C1999%7C199%7C185%7C1750%7C175%7C170%7C165%7C1500%7C150%7C15%7C1499%7C149%7C135%7C1300%7C1299%7C1250%7C125%7C1199%7C105%7C10000%7C1000%7C100%7C10&brand=Black+Diamond&page='+str(i))

	for i in range(1,6):
		baseLinks.append('https://marketplace.beckett.com/search_new/?sport=185225&condition_id=NM-MT&rowNum=250&team=Winnipeg+Jets%7CWashington+Capitals%7CVegas+Golden+Knights%7CVancouver+Canucks%7CToronto+Maple+Leafs%7CToronto+Blue+Jays%7CTeam+USA+HK%7CTeam+Canada+HK%7CTampa+Bay+Lightning%7CSt.+Louis+Blues%7CSan+Jose+Sharks%7CQuebec+Nordiques%7CPittsburgh+Steelers%7CPittsburgh+Pirates%7CPittsburgh+Penguins%7CPhoenix+Roadrunners%7CPhoenix+Coyotes%7CPhiladelphia+Flyers%7COttawa+Senators%7CNew+York+Rangers%7CNew+York+Islanders%7CNew+York+Giants+FB%7CNew+Jersey+Devils%7CNashville+Predators%7CMontreal+Canadiens%7CMinnesota+Wild%7CMinnesota+North+Stars%7CLos+Angeles+Kings%7CHouston+Aeros%7CHartford+Whalers%7CFlorida+Panthers%7CEdmonton+Oilers%7CDetroit+Red+Wings%7CDallas+Stars%7CColumbus+Blue+Jackets%7CColorado+Rockies+HK%7CColorado+Avalanche%7CCleveland+Barons%7CChicago+Blackhawks%7CCarolina+Hurricanes%7CCanada%7CCalifornia+Golden+Seals%7CCalgary+Flames%7CBuffalo+Sabres%7CBoston+Bruins%7CAtlanta+Thrashers%7CAtlanta+Flames%7CArizona+Coyotes%7CAngers+SCO%7CAnaheim+Ducks&marketplace_category_id=Cards+-+Sports&attr=Stick%7CSer%7CRC%7CPromo%7CPatch%7CPads%7CMem8%7CMem4%7CMem3%7CMem2%7CMem%7CJsy%7CAuto2%7CAuto+Sticker%7CAuto+On+Card%7CAuto+Cut%7CAuto&print_run=999%7C99%7C9500%7C950%7C949%7C94%7C900%7C90%7C899%7C89%7C875%7C850%7C85%7C849%7C83%7C825%7C800%7C80%7C799%7C780%7C775%7C750%7C75%7C74%7C70%7C699%7C6950%7C65%7C62%7C6199%7C600%7C60%7C599%7C575%7C55%7C54%7C5000%7C500%7C50%7C499%7C49%7C480%7C4750%7C45%7C4299%7C425%7C400%7C40%7C3999%7C399%7C3900%7C390%7C375%7C3500%7C350%7C35%7C349%7C3475%7C325%7C3099%7C3000%7C300%7C2999%7C299%7C290%7C275%7C2625%7C260%7C2599%7C2500%7C250%7C25%7C249%7C2400%7C225%7C2000%7C200%7C1999%7C199%7C185%7C1750%7C175%7C170%7C165%7C1500%7C150%7C15%7C1499%7C149%7C135%7C1300%7C1299%7C1250%7C125%7C1199%7C105%7C10000%7C1000%7C100%7C10&brand=Crown+Royale&page='+str(i))

	return baseLinks

	
outFilePtr = 'card_data_All.csv'
saveLinkFilePtr = 'save_link.txt'

baseLinks = get_links()

print(len(baseLinks))

for link in baseLinks:
	cards = scrape_cards(link)

	with open(outFilePtr, 'a', newline='') as outfile:
		writer = csv.writer(outfile)
		for card in cards:
			writer.writerow(card)
			
	with open(saveLinkFilePtr, 'w', newline='') as outfile:
		outfile.write(link)
