class QSO:
	"""description of class"""

	def __init__(self):
		#pass
		self.initQSO()

	def initQSO(self):
		self.QSOdate = "__________"
		self.QSOstart = "________"
		self.QSOend = "________"
		self.QSOfreq = "____"
		self.QSOmode = "____"
		self.QSOcall = "______"
		self.QSOrptrx = "___"
		self.QSOrpttx = "___"
		self.QSOlochis = "____"
		self.QSOlocmy = "____"
		self.QSOdist = -1
		self.QSObear = -1


	def printQSO(self):
		print(self.QSOdate +";"+ self.QSOstart +";"+ self.QSOend +";"+ self.QSOfreq +";"+ self.QSOmode +";"+ self.QSOcall +";"+ self.QSOrpttx +";"+ self.QSOrptrx +";"+ self.QSOlochis)
		
	def logQSO(self):
		strLogData = self.QSOdate +";"+ self.QSOstart +";"+ self.QSOend +";"+ self.QSOfreq +";"+ self.QSOmode +";"+ self.QSOcall +";"+ self.QSOrpttx +";"+ self.QSOrptrx +";"+ self.QSOlochis+"\n"
		self.initQSO()
		return strLogData

