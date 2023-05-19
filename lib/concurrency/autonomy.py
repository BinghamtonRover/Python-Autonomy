import time
import cv2
import threading

from network.generated import *

class AutonomyThread(threading.Thread):
	def __init__(self, collection): 
		super().__init__()
		self.collection = collection
		self.keep_alive = True

	def run(self): 
		print(f'"Navigating" to {self.command.destination}')
		camera = cv2.VideoCapture(1)
		temp = True
		while True: 
			if not self.keep_alive: return
			try: 
				success, frame = camera.read()
				if not success: raise "Oh no!"
				self.collection.video.send_frame(camera_id=0, frame=frame, name=CameraName.ROVER_FRONT)
				data = AutonomyData(
					state=AutonomyState.PATHING if temp else AutonomyState.DRIVING, 
					obstacles = [
						GpsCoordinates(latitude=1, longitude=1),
						GpsCoordinates(latitude=1, longitude=2),
						GpsCoordinates(latitude=2, longitude=1),
					],
					path = [
						GpsCoordinates(latitude=0, longitude=1),
						GpsCoordinates(latitude=0, longitude=2),
						GpsCoordinates(latitude=0, longitude=3),
						GpsCoordinates(latitude=1, longitude=3),
					],
					task=self.command.task,
					destination=self.command.destination,
				)
				temp = not temp
				self.collection.data.send_message(data)
				time.sleep(0.1)
			except KeyboardInterrupt: break
			except OSError as error: 
				if error.errno in [10040, 101]: print("Network error")
				else: raise error

	def close(self): 
		self.keep_alive = False
