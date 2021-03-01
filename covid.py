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
	rangeSize = 7
	mm = [0] * (rangeSize // 2)
	for i in range(len(arr)-rangeSize+1):
		mm.append(np.average(arr[i:i+rangeSize]))
	return mm


def plotConMediaMobile(arr, colore):
	mm = mediaMobile(arr)
	plt.plot(arr, linewidth=0.5, color=colore+"77")
	plt.plot(mm, linewidth=1.2, color=colore+"ff")

def plotLineaZero(colore):
	plt.plot([0 for i in range(len(data.nuovi_positivi))], linewidth=0.5, color=colore+"77")

def plotPercentualePositivi(colore):
	incrementoTamponi = incremento(data.tamponi)
	incrementoTamponi[0] = incrementoTamponi[1]
	incrementoTamponi[297] = (incrementoTamponi[296] + incrementoTamponi[298]) / 2
	plotConMediaMobile(np.multiply(np.divide(data.nuovi_positivi, incrementoTamponi), 50000), colore)


data = Data()
plotConMediaMobile(data.nuovi_positivi, "#ff0000")
plotConMediaMobile(incremento(data.nuovi_positivi), "#bb0000")
plotPercentualePositivi("#00ff00")
plotConMediaMobile(data.totale_ospedalizzati, "#0000ff")
plotConMediaMobile(incremento(data.totale_ospedalizzati), "#0000bb")
plotLineaZero("#000000")
plt.show()
