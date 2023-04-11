from network.src.generated.Protobuf.drive_pb2 import DriveCommand

class TankDrive: 
	def __init__(self): 
		self.throttle = 0
		self.left = 0
		self.right = 0

	def handle_command(self, command: DriveCommand): 
		if command.set_throttle: self.throttle = command.throttle
		if command.set_left: self.left = command.left
		if command.set_right: self.right = command.right
		self.update_motors()

	def update_motors(self): 
		# Writes commands to the ESC
		print(f"Writing throttle={self.throttle}, left={self.left}, right={self.right}")
