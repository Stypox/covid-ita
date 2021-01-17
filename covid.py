import requests
import numpy as np
import matplotlib.pyplot as plt

JSON_ITA_URL = "https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-json/dpc-covid19-ita-andamento-nazionale.json"

class Data:
	def __init__(self):
		json = requests.get(JSON_ITA_URL).json()
		def buildArray(key):
			return [0 if e[key] is None else int(e[key]) for e in json]

		self.data = [e["data"] for e in json]
		self.ricoverati_con_sintomi = buildArray("ricoverati_con_sintomi")
		self.terapia_intensiva = buildArray("terapia_intensiva")
		self.totale_ospedalizzati = buildArray("totale_ospedalizzati")
		self.ingressi_terapia_intensiva = buildArray("ingressi_terapia_intensiva")

		self.isolamento_domiciliare = buildArray("isolamento_domiciliare")
		self.deceduti = buildArray("deceduti")
		self.dimessi_guariti = buildArray("dimessi_guariti")

		self.nuovi_positivi = buildArray("nuovi_positivi")
		self.variazione_totale_positivi = buildArray("variazione_totale_positivi")
		self.totale_positivi = buildArray("totale_positivi")
		self.totale_casi = buildArray("totale_casi")

		self.tamponi = buildArray("tamponi")
		self.casi_testati = buildArray("casi_testati")


def incremento(arr):
	inc = [0]
	for i in range(len(arr)-1):
		inc.append(arr[i+1] - arr[i])
	return inc

def mediaMobile(arr):
	mm = [0, 0, 0]
	for i in range(len(arr)-7+1):
		mm.append(int(np.average(arr[i:i+7])))
	return mm


def plotConMediaMobile(arr, colore):
	mm = mediaMobile(arr)
	plt.plot(arr, color=colore+"66")
	plt.plot(mm, color=colore+"ff")

def plotLineaZero(arr, colore):
	plt.plot([0 for i in range(len(arr))], color=colore+"66")


data = Data()
a = data.nuovi_positivi

plotConMediaMobile(a, "#ff0000")
plotConMediaMobile(incremento(a), "#0000ff")
#plotConMediaMobile(incremento(incremento(a)), "#00ff00")
plotLineaZero(a, "#000000")
plt.show()
