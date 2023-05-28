from network import *

from lib.cameras import *
from lib.hardware import *
from lib.network import *
from lib.thread import *

class AutonomyCollection: 
	def __init__(self):
		print("[Info] Initializing Autonomy")

		# Sockets
		print("[Info] Initializing network...")
		self.subsystems = AutonomyDataServer(port=8003)
		self.video = AutonomyVideoServer(port=8002)
		self.dashboard = AutonomyServer(port=8004, collection=self)

		# Hardware control
		print("[Info] Initializing hardware...")
		self.drive = Drive(collection=self)
		self.gps = GpsThread(collection=self)
		self.imu = ImuThread(collection=self)
		self.depth_camera = DepthCameraThread(collection=self)
		self.camera = ObstacleDetectionCamera(1.8, 240, -0.3, self.depth_camera)

		# Main process
		print("[Info] Initializing main thread...")
		self.autonomy = AutonomyThread(collection=self)

		print("[Info] Autonomy initialized")

	def close(self):  # close everything in reverse order
		self.drive.close()
		self.autonomy.close()
		self.camera.close()
		self.imu.close()
		self.gps.close()
		self.subsystems.close_socket()
		self.video.close_socket()
		self.dashboard.close_socket()

	def start(self): 
		ServerThread.startThreads([self.dashboard, self.video, self.subsystems, self.gps, self.imu, self.autonomy])

if __name__ == "__main__":
	autonomy = AutonomyCollection()
	autonomy.start()
	autonomy.close()
