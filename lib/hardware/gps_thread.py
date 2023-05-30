import gps
import threading
import sys
import time
import random

from network.generated import GpsCoordinates, RoverPosition

class MockGps: 
	def __init__(self): 
		print("[Warning] Using mock GPS on non-Linux platform")

	def next(self): 
		return {"class": "TPV", "lat": random.random() * 10 - 5, "lon": random.random() * 10 - 5}

	def stream(self, *args): pass

class GpsThread(threading.Thread):
	def __init__(self, collection, test=False):
		print("[Info] Initializing GPS...")
		super().__init__()
		self.keep_alive = True
		if test or sys.platform != "linux":
			self.session = MockGps()
		else: 
			self.session = gps.gps("localhost", "2947")
		self.session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)
		self.collection = collection
		self.coordinates = GpsCoordinates()

	def close(self): 
		self.keep_alive = False

	# TODO: Remove in favor of directly accessing self.coordinates
	def read_gps(self):
			return (self.lat, self.long)

	def run(self):
		while self.keep_alive:
			gps_data = self.session.next()
			if gps_data["class"] != "TPV": continue
			self.lat = gps_data['lat']
			self.long = gps_data['lon']
			self.coordinates = GpsCoordinates(latitude=self.lat, longitude=self.long)
			message = RoverPosition(gps=self.coordinates)
			self.collection.dashboard.send_message(message)
			time.sleep(0.5)
