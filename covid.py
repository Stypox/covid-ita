import requests
import numpy as np
import matplotlib.pyplot as plt
import time
import datetime

JSON_ITA_URL = "https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-json/dpc-covid19-ita-andamento-nazionale.json"
JSON_VACCINI_ITA_URL = "https://raw.githubusercontent.com/italia/covid19-opendata-vaccini/master/dati/somministrazioni-vaccini-summary-latest.json"
JSON_REGIONI_ITA_URL = "https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-json/dpc-covid19-ita-regioni.json"

def dateStringToObject(dateString):
	return datetime.date(int(dateString[:4]), int(dateString[5:7]), int(dateString[8:10]))

class DataRegione:
	def __init__(self, startingDate, arrayLength, code, name):
		def buildArray():
			return [0 for i in range(arrayLength)]

		self.startingDate = startingDate
		self.code = code
		self.name = name

		self.ricoverati_con_sintomi = buildArray()
		self.terapia_intensiva = buildArray()
		self.totale_ospedalizzati = buildArray()
		self.isolamento_domiciliare = buildArray()
		self.totale_positivi = buildArray()
		self.variazione_totale_positivi = buildArray()
		self.nuovi_positivi = buildArray()
		self.dimessi_guariti = buildArray()
		self.deceduti = buildArray()
		self.totale_casi = buildArray()
		self.tamponi = buildArray()
		self.casi_testati = buildArray()
		self.ingressi_terapia_intensiva = buildArray()

	def addDataPoint(self, jsonObject):
		date = dateStringToObject(jsonObject["data"])
		i = (date - self.startingDate).days
		for key, value in jsonObject.items():
			if hasattr(self, key):
				getattr(self, key)[i] = (0 if value is None else int(value))


class Data:
	def __init__(self):
		json = requests.get(JSON_ITA_URL).json()
		def buildArray(key):
			return [0 if e[key] is None else int(e[key]) for e in json]

		self.date = [dateStringToObject(e["data"]) for e in json]
		self.ricoverati_con_sintomi = buildArray("ricoverati_con_sintomi")
		self.terapia_intensiva = buildArray("terapia_intensiva")
		self.totale_ospedalizzati = buildArray("totale_ospedalizzati")
		self.isolamento_domiciliare = buildArray("isolamento_domiciliare")
		self.totale_positivi = buildArray("totale_positivi")
		self.variazione_totale_positivi = buildArray("variazione_totale_positivi")
		self.nuovi_positivi = buildArray("nuovi_positivi")
		self.dimessi_guariti = buildArray("dimessi_guariti")
		self.deceduti = buildArray("deceduti")
		self.totale_casi = buildArray("totale_casi")
		self.tamponi = buildArray("tamponi")
		self.casi_testati = buildArray("casi_testati")
		self.ingressi_terapia_intensiva = buildArray("ingressi_terapia_intensiva")

		jsonVaccini = requests.get(JSON_VACCINI_ITA_URL).json()["data"]
		self.nuovi_vaccini = [0 for _ in range(len(json))]
		for dataPoint in jsonVaccini:
			dateSomministrazione = dateStringToObject(dataPoint["data_somministrazione"])
			self.nuovi_vaccini[(dateSomministrazione - self.date[0]).days] += dataPoint["totale"]
		self.nuovi_vaccini = np.trim_zeros(self.nuovi_vaccini, 'b') # remove zeros at end

		jsonRegioni = requests.get(JSON_REGIONI_ITA_URL).json()
		self.piemonte = DataRegione(self.date[0], len(json), 1, "Piemonte")
		self.valle_d_aosta = DataRegione(self.date[0], len(json), 2, "Valle d'Aosta")
		self.lombardia = DataRegione(self.date[0], len(json), 3, "Lombardia")
		self.veneto = DataRegione(self.date[0], len(json), 5, "Veneto")
		self.friuli_venezia_giulia = DataRegione(self.date[0], len(json), 6, "Friuli Venezia Giulia")
		self.liguria = DataRegione(self.date[0], len(json), 7, "Liguria")
		self.emilia_romagna = DataRegione(self.date[0], len(json), 8, "Emilia Romagna")
		self.toscana = DataRegione(self.date[0], len(json), 9, "Toscana")
		self.umbria = DataRegione(self.date[0], len(json), 10, "Umbria")
		self.marche = DataRegione(self.date[0], len(json), 11, "Marche")
		self.lazio = DataRegione(self.date[0], len(json), 12, "Lazio")
		self.abruzzo = DataRegione(self.date[0], len(json), 13, "Abruzzo")
		self.molise = DataRegione(self.date[0], len(json), 14, "Molise")
		self.campania = DataRegione(self.date[0], len(json), 15, "Campania")
		self.puglia = DataRegione(self.date[0], len(json), 16, "Puglia")
		self.basilicata = DataRegione(self.date[0], len(json), 17, "Basilicata")
		self.calabria = DataRegione(self.date[0], len(json), 18, "Calabria")
		self.sicilia = DataRegione(self.date[0], len(json), 19, "Sicilia")
		self.sardegna = DataRegione(self.date[0], len(json), 20, "Sardegna")
		self.alto_adige = DataRegione(self.date[0], len(json), 21, "Alto Adige")
		self.trentino = DataRegione(self.date[0], len(json), 22, "Trentino")
		self.regioni = [self.piemonte, self.valle_d_aosta, self.lombardia, self.veneto, self.friuli_venezia_giulia, self.liguria,
			self.emilia_romagna, self.toscana, self.umbria, self.marche, self.lazio, self.abruzzo, self.abruzzo, self.molise,
			self.campania, self.puglia, self.basilicata, self.calabria, self.sicilia, self.sardegna, self.alto_adige, self.trentino]
		for dataPoint in jsonRegioni:
			for regione in self.regioni:
				if regione.code == dataPoint["codice_regione"]:
					regione.addDataPoint(dataPoint)


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
	plt.plot_date(data.date[0:len(arr)], arr, linewidth=0.5, color=colore+"77", fmt="b-")
	plt.plot_date(data.date[0:len(mm)], mm, linewidth=1.2, color=colore+"ff", fmt="b-")

def plotLineaZero(colore):
	plt.plot_date(data.date[0:len(data.nuovi_positivi)], [0 for i in range(len(data.nuovi_positivi))], linewidth=0.5, color=colore+"77", fmt="b-")

def plotPercentualePositivi(colore):
	incrementoTamponi = incremento(data.tamponi)
	incrementoTamponi[0] = incrementoTamponi[1]
	incrementoTamponi[297] = (incrementoTamponi[296] + incrementoTamponi[298]) / 2
	plotConMediaMobile(np.multiply(np.divide(data.nuovi_positivi, incrementoTamponi), 50000), colore)


data = Data()
plotConMediaMobile(data.trentino.nuovi_positivi, "#ff0000")
plotConMediaMobile(incremento(data.trentino.nuovi_positivi), "#bb0000")
plotPercentualePositivi("#aaaa00")
plotConMediaMobile(data.totale_ospedalizzati, "#0000ff")
plotConMediaMobile(incremento(data.totale_ospedalizzati), "#0000bb")
plotConMediaMobile(data.nuovi_vaccini, "#00ff00")
plotLineaZero("#000000")

plt.xticks(rotation=90)
plt.show()
