from network import ProtoSocket, Device
from network.src.generated.Protobuf.drive_pb2 import *

class Drive: 
	"""A service to manage drive controls.

	This class only sends messages to the subsystems program, whether it is running on the tank or the
	rover. The only thing that changes is the IP address of the Subsystems program, which is why this
	class takes a [socket] paramter as input.

	- To change the top speed of the tank, use [set_throttle]
	- To manually control each wheel, use [set_speeds]
	"""
	def __init__(self, socket): 
		self.socket = socket

	def set_throttle(self, throttle): 
		#print(f"Setting throttle to {throttle}")
		command = DriveCommand(set_throttle=True, throttle=throttle)
		self.socket.send_message(command)

	def set_speeds(self, left, right): 
		#print(f"Setting left={left}, right={right}")
		command = DriveCommand(set_left=True, left=left, set_right=True, right=right)
		self.socket.send_message(command)
