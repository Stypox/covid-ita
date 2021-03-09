import requests
import numpy as np
import matplotlib.pyplot as plt
import time
import datetime

JSON_ITA_URL = "https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-json/dpc-covid19-ita-andamento-nazionale.json"
JSON_VACCINI_ITA_URL = "https://raw.githubusercontent.com/italia/covid19-opendata-vaccini/master/dati/somministrazioni-vaccini-summary-latest.json"

def dateStringToObject(dateString):
	return datetime.date(int(dateString[:4]), int(dateString[5:7]), int(dateString[8:10]))

class Data:
	def __init__(self):
		json = requests.get(JSON_ITA_URL).json()
		def buildArray(key):
			return [0 if e[key] is None else int(e[key]) for e in json]

		self.data = [dateStringToObject(e["data"]) for e in json]
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

		jsonVaccini = requests.get(JSON_VACCINI_ITA_URL).json()["data"]
		self.nuovi_vaccini = [0 for _ in range(len(json))]
		for dataPoint in jsonVaccini:
			dateSomministrazione = dateStringToObject(dataPoint["data_somministrazione"])
			self.nuovi_vaccini[(dateSomministrazione - self.data[0]).days] += dataPoint["totale"]
		self.nuovi_vaccini = np.trim_zeros(self.nuovi_vaccini, 'b') # remove zeros at end


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
	plt.plot_date(data.data[0:len(arr)], arr, linewidth=0.5, color=colore+"77", fmt="b-")
	plt.plot_date(data.data[0:len(mm)], mm, linewidth=1.2, color=colore+"ff", fmt="b-")

def plotLineaZero(colore):
	plt.plot_date(data.data[0:len(data.nuovi_positivi)], [0 for i in range(len(data.nuovi_positivi))], linewidth=0.5, color=colore+"77", fmt="b-")

def plotPercentualePositivi(colore):
	incrementoTamponi = incremento(data.tamponi)
	incrementoTamponi[0] = incrementoTamponi[1]
	incrementoTamponi[297] = (incrementoTamponi[296] + incrementoTamponi[298]) / 2
	plotConMediaMobile(np.multiply(np.divide(data.nuovi_positivi, incrementoTamponi), 50000), colore)


data = Data()
plotConMediaMobile(data.nuovi_positivi, "#ff0000")
plotConMediaMobile(incremento(data.nuovi_positivi), "#bb0000")
plotPercentualePositivi("#aaaa00")
plotConMediaMobile(data.totale_ospedalizzati, "#0000ff")
plotConMediaMobile(incremento(data.totale_ospedalizzati), "#0000bb")
plotConMediaMobile(data.nuovi_vaccini, "#00ff00")
plotLineaZero("#000000")

plt.xticks(rotation=90)
plt.show(block=False)
while True:
	plt.tight_layout()
	plt.gcf().canvas.flush_events()
	time.sleep(0.01)
