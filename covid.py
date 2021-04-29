import requests
import numpy as np
import matplotlib.pyplot as plt
import time
import datetime

JSON_ITALIA_URL = "https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-json/dpc-covid19-ita-andamento-nazionale.json"
JSON_VACCINI_URL = "https://raw.githubusercontent.com/italia/covid19-opendata-vaccini/master/dati/somministrazioni-vaccini-summary-latest.json"
JSON_REGIONI_URL = "https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-json/dpc-covid19-ita-regioni.json"

def dateStringToObject(dateString):
	return datetime.date(int(dateString[:4]), int(dateString[5:7]), int(dateString[8:10]))

class DataRegione:
	def __init__(self, firstDay, dayCount, code, name):
		def buildArray():
			return [0 for i in range(dayCount)]

		self.firstDay = firstDay
		self.dayCount = dayCount
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
		self.nuovi_vaccini = buildArray()
		self.percentuale_positivi = buildArray()

	def isCode(self, code):
		if isinstance(self.code, list):
			return code in self.code
		return code == self.code

	def addDataPoint(self, jsonObject):
		date = dateStringToObject(jsonObject["data"])
		i = (date - self.firstDay).days
		for key, value in jsonObject.items():
			if hasattr(self, key):
				getattr(self, key)[i] = (0 if value is None else int(value))

	def addVaccino(self, jsonObject):
		date = dateStringToObject(jsonObject["data_somministrazione"])
		i = (date - self.firstDay).days

		if i == len(self.nuovi_vaccini):
			self.nuovi_vaccini.append(0)
		elif i > len(self.nuovi_vaccini):
			print("Nuovi vaccini troppo nel futuro: " + date)

		self.nuovi_vaccini[i] += jsonObject["totale"]

	def finalize(self):
		# togliere zeri in fondo TODO non togliere zero reali
		self.ricoverati_con_sintomi = np.trim_zeros(self.ricoverati_con_sintomi, 'b')
		self.terapia_intensiva = np.trim_zeros(self.terapia_intensiva, 'b')
		self.totale_ospedalizzati = np.trim_zeros(self.totale_ospedalizzati, 'b')
		self.isolamento_domiciliare = np.trim_zeros(self.isolamento_domiciliare, 'b')
		self.totale_positivi = np.trim_zeros(self.totale_positivi, 'b')
		self.variazione_totale_positivi = np.trim_zeros(self.variazione_totale_positivi, 'b')
		self.nuovi_positivi = np.trim_zeros(self.nuovi_positivi, 'b')
		self.dimessi_guariti = np.trim_zeros(self.dimessi_guariti, 'b')
		self.deceduti = np.trim_zeros(self.deceduti, 'b')
		self.totale_casi = np.trim_zeros(self.totale_casi, 'b')
		self.tamponi = np.trim_zeros(self.tamponi, 'b')
		self.casi_testati = np.trim_zeros(self.casi_testati, 'b')
		self.ingressi_terapia_intensiva = np.trim_zeros(self.ingressi_terapia_intensiva, 'b')

		# rimuovere l'ultima giornata dei vaccini, di solito non e' ancora a posto
		self.nuovi_vaccini = np.trim_zeros(self.nuovi_vaccini, 'b')
		self.nuovi_vaccini = self.nuovi_vaccini[:min(len(self.nuovi_vaccini), self.dayCount - 1)]

		# calcolo percentuale positivi
		incrementoTamponi = incremento(self.tamponi)
		for i in range(1, min(len(self.nuovi_positivi), len(incrementoTamponi))):
			if self.nuovi_positivi[i] >= incrementoTamponi[i] or incrementoTamponi[i] == 0:
				self.percentuale_positivi[i] = self.percentuale_positivi[i-1]
			else:
				self.percentuale_positivi[i] = self.nuovi_positivi[i] / incrementoTamponi[i]
				if (abs(self.percentuale_positivi[i] - self.percentuale_positivi[i-1]) > 0.2):
					average = (self.percentuale_positivi[i] + self.percentuale_positivi[i-1]) / 2
					self.percentuale_positivi[i] = average
					self.percentuale_positivi[i-1] = average
		self.percentuale_positivi = np.trim_zeros(self.percentuale_positivi, 'b')


class Data:
	def __init__(self):

		jsonItalia = requests.get(JSON_ITALIA_URL).json()
		self.date = [dateStringToObject(e["data"]) for e in jsonItalia]
		firstDay = self.date[0]
		dayCount = len(jsonItalia)
		self.numero_giorni = dayCount

		self.piemonte = DataRegione(firstDay, dayCount, 1, "Piemonte")
		self.valle_d_aosta = DataRegione(firstDay, dayCount, 2, "Valle d'Aosta")
		self.lombardia = DataRegione(firstDay, dayCount, 3, "Lombardia")
		self.veneto = DataRegione(firstDay, dayCount, 5, "Veneto")
		self.friuli_venezia_giulia = DataRegione(firstDay, dayCount, 6, "Friuli Venezia Giulia")
		self.liguria = DataRegione(firstDay, dayCount, 7, "Liguria")
		self.emilia_romagna = DataRegione(firstDay, dayCount, 8, "Emilia Romagna")
		self.toscana = DataRegione(firstDay, dayCount, 9, "Toscana")
		self.umbria = DataRegione(firstDay, dayCount, 10, "Umbria")
		self.marche = DataRegione(firstDay, dayCount, 11, "Marche")
		self.lazio = DataRegione(firstDay, dayCount, 12, "Lazio")
		self.abruzzo = DataRegione(firstDay, dayCount, 13, "Abruzzo")
		self.molise = DataRegione(firstDay, dayCount, 14, "Molise")
		self.campania = DataRegione(firstDay, dayCount, 15, "Campania")
		self.puglia = DataRegione(firstDay, dayCount, 16, "Puglia")
		self.basilicata = DataRegione(firstDay, dayCount, 17, "Basilicata")
		self.calabria = DataRegione(firstDay, dayCount, 18, "Calabria")
		self.sicilia = DataRegione(firstDay, dayCount, 19, "Sicilia")
		self.sardegna = DataRegione(firstDay, dayCount, 20, "Sardegna")
		self.alto_adige = DataRegione(firstDay, dayCount, 21, "Alto Adige")
		self.trentino = DataRegione(firstDay, dayCount, [22, 4], "Trentino")
		self.regioni = [self.piemonte, self.valle_d_aosta, self.lombardia, self.veneto, self.friuli_venezia_giulia, self.liguria,
			self.emilia_romagna, self.toscana, self.umbria, self.marche, self.lazio, self.abruzzo, self.abruzzo, self.molise,
			self.campania, self.puglia, self.basilicata, self.calabria, self.sicilia, self.sardegna, self.alto_adige, self.trentino]
		self.italia = DataRegione(firstDay, dayCount, -1, "Tutta Italia")

		for dataPoint in jsonItalia:
			self.italia.addDataPoint(dataPoint)

		jsonVaccini = requests.get(JSON_VACCINI_URL).json()["data"]
		for dataPoint in jsonVaccini:
			self.italia.addVaccino(dataPoint)
			for regione in self.regioni:
				if regione.isCode(dataPoint["codice_regione_ISTAT"]):
					regione.addVaccino(dataPoint)
		self.italia.finalize()

		jsonRegioni = requests.get(JSON_REGIONI_URL).json()
		for dataPoint in jsonRegioni:
			for regione in self.regioni:
				if regione.isCode(dataPoint["codice_regione"]):
					regione.addDataPoint(dataPoint)
		for regione in self.regioni:
			regione.finalize()


def incremento(arr):
	inc = [0]
	for i in range(len(arr)-1):
		inc.append(arr[i+1] - arr[i])
	return inc

def mediaMobile(arr, giorni):
	rangeSize = giorni
	mm = [0] * (rangeSize // 2)
	for i in range(len(arr)-rangeSize+1):
		mm.append(np.average(arr[i:i+rangeSize]))
	return mm



def plotConMediaMobile(subplot, arr, giorni, colore, label, addTotalToLabel=False):
	label = f"{label} - Tot {int(np.sum(arr)):,d}" if addTotalToLabel else label
	mm = mediaMobile(arr, giorni)
	subplot.plot_date(d.date[0:len(arr)], arr, linewidth=0.5, color=colore+"77", fmt="b-")
	return subplot.plot_date(d.date[0:len(mm)], mm, linewidth=1.2, color=colore+"ff", fmt="b-", label=label)

def setupSubplots(subplots):
	for subplot in subplots:
		# line at y=0
		subplot.axhline(y=0, color="#00000077")
		plt.sca(subplot)
		plt.xticks(rotation=90)
		plt.legend(loc=0)

def plot(regione):
	_, axis = plt.subplots(2, 2, num=regione.name)

	plotConMediaMobile(axis[0, 0], regione.nuovi_positivi, 7, "#ff0000", "Nuovi positivi", True)
	plotConMediaMobile(axis[0, 0], regione.totale_ospedalizzati, 7, "#0000ff", "Totale ospedalizzati")
	plotConMediaMobile(axis[0, 0], incremento(regione.deceduti), 7, "#00aaaa", "Nuovi deceduti", True)

	plotConMediaMobile(axis[0, 1], incremento(regione.nuovi_positivi), 14, "#bb0000", "Nuovi positivi - incremento")
	plotConMediaMobile(axis[0, 1], incremento(regione.totale_ospedalizzati), 7, "#0000bb", "Totale ospedalizzati - incremento")

	line1 = plotConMediaMobile(axis[1, 0], regione.percentuale_positivi, 7, "#aaaa00", "Percentuale positivi")
	line2 = plotConMediaMobile(axis[1, 0], incremento(regione.percentuale_positivi), 7, "#555500", "Percentuale positivi - incremento")
	axisTamponi = axis[1, 0].twinx()
	line3 = plotConMediaMobile(axisTamponi, incremento(regione.tamponi), 7, "#aa00aa", "Tamponi", True)

	plotConMediaMobile(axis[1, 1], regione.nuovi_vaccini, 7, "#00ff00", "Nuovi vaccini", True)
	plotConMediaMobile(axis[1, 1], incremento(regione.nuovi_vaccini), 7, "#00bb00", "Nuovi vaccini - incremento")

	setupSubplots([axis[0,0], axis[0,1], axis[1,0], axis[1,1]])

	plt.sca(axis[0, 1])
	maxIncrementoNuoviPositivi = max(mediaMobile(incremento(regione.nuovi_positivi), 7))
	plt.ylim(-1.2*maxIncrementoNuoviPositivi, 1.2*maxIncrementoNuoviPositivi)

	plt.sca(axis[1, 0])
	plt.ylim(bottom=-0.03)
	linesWithCommonLegend = line1 + line2 + line3
	plt.legend(linesWithCommonLegend, [line.get_label() for line in linesWithCommonLegend])

	plt.sca(axis[1, 1])
	plt.xlim(datetime.date(2020, 12, 22), datetime.date.today())
	plt.ylim(bottom=-max(regione.nuovi_vaccini + [0])/10)

	plt.tight_layout()
	plt.draw()

d = Data()
plot(d.italia)
plt.show()
