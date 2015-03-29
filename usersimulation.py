import time
import numpy
import random
import requests

class AutoPoster:


	def __init__(self, username, groupname, expectedDelay, descriptions):
		self.user=username
		self.group=groupname
		self.exponential=expectedDelay
		self.descs = descriptions
		self.currentWait = self.generateWait()
		self.baseUrl = "http://sighting-env.elasticbeanstalk.com/"

	def generateWait(self):
		return numpy.random.exponential(self.exponential)

	def isReady(self,inc):
		self.currentWait=self.currentWait-inc
		if(self.currentWait<0):
			self.currentWait = self.generateWait()
			return True

	def rndDesc(self):
		return self.descs[random.randint(0,len(self.descs)-1)]


	def register(self):
		r = requests.get(self.baseUrl+"register",params={'user':self.user,'pass':"bot"})
		print r.text
		r = requests.get(self.baseUrl+"join",params={'user':self.user,'group':self.group,'description':'This group is maintained by a bot','status':5})
		print r.text

	def rndLat(self):
		return 40.4397+random.uniform(-0.05,0.05)

	def rndLng(self):
		return -79.9764+random.uniform(-0.05,0.05)

	def doAlert(self):
		r = requests.get(self.baseUrl+"add_alert",params={'user':self.user,'group':self.group,'title':self.rndDesc(),'lat':self.rndLat(),'lng':self.rndLng()})
		print r.text

def main():
	autoposters = []

	diseases = ["Flu outbreak!","Measles spreading","Flu symptoms reported","Common cold symptoms reported","Caution advised"]
	diseasePoster = AutoPoster("Germaphobe","Disease",30.0,diseases)
	autoposters.append(diseasePoster)

	crimes = ["Arson","Corruption","Burglary","Disorderly conduct","Forger on the loose!","Shoplifting","Robbery","Tax evasion","Vandalism"]
	crimePoster = AutoPoster("Batman","Crime",60.0,crimes)
	autoposters.append(crimePoster)

	foods = ["Cakes","Tarts","Cookies","Ice cream","Pie","Pudding","Brownies"]
	foodPoster = AutoPoster("SweetTooth","Free food",90.0,foods)
	autoposters.append(foodPoster)

	for poster in autoposters:
		poster.register()

	while(True):
		time.sleep(1)
		for poster in autoposters:
			if poster.isReady(1.0):
				poster.doAlert()

if __name__ == "__main__":
	main()
