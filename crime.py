import time
import numpy
import random
import requests
import json
class AutoPoster:


	def __init__(self, username, groupname, source): # initializes variables
		self.user=username
		self.group=groupname
		self.source=source
		self.baseUrl = "http://sighting-env.elasticbeanstalk.com/"
		self.alreadyPosted = [] # array for storing posted alerts

	def register(self):
		r = requests.get(self.baseUrl+"register",params={'user':self.user,'pass':"bot"})
		print r.text
		r = requests.get(self.baseUrl+"join",params={'user':self.user,'group':self.group,'description':'This group is maintained by a bot','status':5})
		print r.text

	def checkAlert(self):
		r = requests.get(self.source)
		data = r.json()
		for crime in data["crimes"]:
			if(not crime["cdid"] in self.alreadyPosted):
				self.alreadyPosted.append(crime["cdid"])
				self.postAlert(crime["type"] + ": " + crime["date"],crime["lat"],crime["lon"])

	def postAlert(self,title,lat,lng): # function to post alerts in app
		r = requests.get(self.baseUrl+"add_alert",params={'user':self.user,'group':self.group,'title':title,'lat':lat,'lng':lng})
		print r.text

def main():
	autoposters = []

	crimePoster = AutoPoster("SpotCrime.com","SpotCrime.com","http://api.spotcrime.com/crimes.json?lat=40.3924362&lon=-79.9553335&radius=1&key=MLC-restricted-key")
	# lat/long data for recent crimes
	autoposters.append(crimePoster)

	for poster in autoposters:
		poster.register()

	while(True):
		for poster in autoposters:
			poster.checkAlert()
		time.sleep(60)

if __name__ == "__main__":
	main()
