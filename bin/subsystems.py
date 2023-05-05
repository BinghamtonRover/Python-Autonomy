from network import ProtoSocket, Device
from network.generated import DriveCommand
from lib.hardware.tank_drive import TankDrive

SUBSYSTEMS_PORT = 8001
AUTONOMY_PORT = 8004

class TankSubsystems(ProtoSocket):
	def __init__(self): 
		self.drive = TankDrive()
		super().__init__(port=SUBSYSTEMS_PORT, device=Device.SUBSYSTEMS)

	def on_disconnect(self):  # overriden
		self.drive.set_throttle(0)		

	def on_message(self, wrapper):  # overriden
		if wrapper.name == "DriveCommand":
			message = DriveCommand.FromString(wrapper.data)
			self.drive.handle_command(message)

if __name__ == "__main__": 
	server = TankSubsystems()
	server.listen()
