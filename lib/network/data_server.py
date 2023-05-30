from network import *
from network.generated import *

class AutonomyDataServer(ProtoSocket):
	def __init__(self, port): 
		super().__init__(port, device=Device.AUTONOMY, destination = ("127.0.0.1", 8001), send_heartbeats=False)
		self.leftSensorValue = None
		self.rightSensorValue = None

	def on_message(self, wrapper):
		if wrapper.name == "DriveData":
			data = DriveData.FromString(wrapper.data)
			if data.leftSensorValue != 0: self.leftSensorValue = data.leftSensorValue
			if data.rightSensorValue!= 0: self.rightSensorValue = data.rightSensorValue
