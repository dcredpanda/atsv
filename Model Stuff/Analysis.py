from sklearn.preprocessing import normalize
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def graph_feature(x,y,label='something'):
	plt.scatter(x, y, color='g', alpha=1, label=label)
	plt.xlabel('x')
	plt.ylabel('y')
	plt.legend()
	plt.show()

inputPtr = 'web_scraper/card_data_All.csv'

data = pd.read_csv(inputPtr, sep=',',header=None)
data = np.array(data)

np.random.shuffle(data)

x = data[...,4:18]
y = data[...,18:]

#x = np.insert(x,0,1,axis=1)
#x = normalize(x)

#Title, playerName, teamName, brand, year, printRun, promo, patch, pads, jsy, aus, auoc, auc, stick, rook, mem, auto, ser, price

graph_feature(x[...,0:1],y,label='year') #Rand
graph_feature(x[...,1:2],y,label='Run') # High cor
graph_feature(x[...,2:3],y,label='promo') # Garbage
graph_feature(x[...,3:4],y,label='patch') # Rand
graph_feature(x[...,4:5],y,label='pads') # garbage
graph_feature(x[...,5:6],y,label='jsy')  # rand
graph_feature(x[...,6:7],y,label='aus') # Nothing
graph_feature(x[...,7:8],y,label='auoc') # Nothing
graph_feature(x[...,8:9],y,label='auc') # Nothing
graph_feature(x[...,9:10],y,label='stick') # Rand
graph_feature(x[...,10:11],y,label='rook') # Pos Corr
graph_feature(x[...,11:12],y,label='mem') # Corr
graph_feature(x[...,12:13],y,label='auto') # Corr
graph_feature(x[...,13:14],y,label='ser') # Corr