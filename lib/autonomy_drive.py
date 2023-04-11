from network import ProtoSocket, Device
from network.src.generated.Protobuf.drive_pb2 import *
''' 
Unanswered questions:
	What proto files encapsulate the compass, gyroscope, and gps data?
'''

THROTTLE_DEFAULT = 0
LEFT_DEFAULT = 0
RIGHT_DEFAULT = 0

DRIVE_COMMAND_NAME = "DriveCommand"
ROVER_ADDRESS = "192.168.1.20"
ROVER_PORT = 8003


#potential class for sending data from AutonomyPi to MainPi
class Rover:
	def __init__(self):
		self.socket = ProtoSocket(port=8004, destination=(ROVER_ADDRESS, ROVER_PORT), device=Device.AUTONOMY)

	def send_compass_data(self, direction):
		pass

	def send_gyroscope_data(self, x, y, z):
		pass

	def send_imu_data(self, x, y, z):
		pass


#potential class for sending data from MainPi to AutonomyPi
class MainPi:
	
	def __init__(self, ip, port, buffer_size):
		set_receiving_pi(ip, port, buffer_size)

	def set_receiving_pi(self, ip, port, buffer_size):
		self.messenger = ProtoClient(ip,port,buffer_size)
	
	def send_gps_data(self, x, y):
		pass
	




