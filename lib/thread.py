import time
import cv2
import threading
from lib.autonomy_main import Autonomy

from network.generated import *

class AutonomyThread(threading.Thread):
	def __init__(self, collection): 
		super().__init__()
		self.collection = collection
		self.camera = cv2.VideoCapture(0)
		self.keep_alive = True
		self.command = None
		self.autonomy = Autonomy()

	def run(self): 
		while self.keep_alive:
			time.sleep(1.0)
		"""
		while self.keep_alive:
			# Read camera and send it to the dashboard
			video = self.collection.video
			if not self.camera.isOpened(): 
				video.send_status(CameraStatus.CAMERA_DISCONNECTED)
				time.sleep(0)
				continue
			success, frame = self.camera.read()
			if not success: 
				print("Camera didn't respond")
			self.collection.video.send_frame(frame=frame, name=CameraName.ROVER_FRONT)

			if self.command is None: continue
			data = AutonomyData(
				state=AutonomyState.PATHING,
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
			self.collection.dashboard.send_message(data)
		"""

	def startTask(self, command): 
		self.command = command
		print(f'"Navigating" to {command.destination}')
		if self.command.task == AutonomyTask.GPS_ONLY:
			self.autonomy.autonomy_to_cords(self.collection)
			self.command = None
		elif self.command.task == AutonomyTask.VISUAL_MARKER:
			self.autonomy.autonomy_to_marker(self.collection)
			self.command = None

	def stopTask(self): 
		self.command = None

	def close(self): 
		self.keep_alive = False
