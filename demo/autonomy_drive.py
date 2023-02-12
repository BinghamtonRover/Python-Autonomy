import proto_sender
#import drive_pb2
#import drive_pb3



''' 
Unanswered questions:
	What proto files encapsulate the compass, gyroscope, and gps data?
'''

THROTTLE_DEFAULT = 0
LEFT_DEFAULT = 0
RIGHT_DEFAULT = 0

DRIVE_COMMAND_NAME = "Drive"


#potential class for sending data from AutonomyPi to MainPi
class AutonomyRover:

	def __init__(self, ip, port, buffer_size):
		set_receiving_pi(ip, port, buffer_size)

	def set_receiving_pi(self, ip, port, buffer_size):
		self.messenger = ProtoSender(ip,port,buffer_size)
	
	def send_drive_data(self, throttle = THROTTLE_DEFAULT, left = LEFT_DEFAULT, right = RIGHT_DEFAULT):
		drive_message = drive_pb2.DriveCommand()
		drive_message.throttle = throttle
		drive_message.left = left
		drive_message.right = right
		self.messenger.send_proto(drive_message, DRIVE_COMMAND_NAME)

	def adjust_throttle(self, throttle = THROTTLE_DEFAULT):
		drive_message = drive_pb2.DriveCommand()
		drive_message.throttle = throttle
		self.messenger.send_proto(drive_message, DRIVE_COMMAND_NAME)

	def adjust_right(self, right = RIGHT_DEFAULT):
		drive_message = drive_pb2.DriveCommand()
		drive_message.right = right
		self.messenger.send_proto(drive_message, DRIVE_COMMAND_NAME)

	def adjust_left(self, left = LEFT_DEFAULT):
		drive_message = drive_pb2.DriveCommand()
		drive_message.left = left
		self.messenger.send_proto(drive_message, DRIVE_COMMAND_NAME)

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
		self.messenger = ProtoSender(ip,port,buffer_size)
	
	def send_gps_data(self, x, y):
		pass
	




