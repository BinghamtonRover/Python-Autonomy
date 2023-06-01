from network import *
from network.generated import *

class AutonomyDataServer(ProtoSocket):
	def __init__(self, port): 
		super().__init__(port, device=Device.AUTONOMY, destination = ("127.0.0.1", 8001), send_heartbeats=False)
		self.leftSensorValue = 0.0
		self.rightSensorValue = 0.0
		self.previousLeftSensorValue = 0.0
		self.previousRightSensorValue = 0.0
		self.drivableDistance = 90.0

	def on_message(self, wrapper):
		if wrapper.name == "DriveData":
			data = DriveData.FromString(wrapper.data)
			if data.leftSensorValue != 0:
				if data.leftSensorValue == -1.0:
					data.leftSensorValue = 9999.0
				self.previousLeftSensorValue = self.leftSensorValue
				self.leftSensorValue = data.leftSensorValue
			if data.rightSensorValue!= 0:
				if data.rightSensorValue == -1.0:
					data.rightSensorValue = 9999.0
				self.previousRightSensorValue = self.rightSensorValue
				self.rightSensorValue = data.rightSensorValue

	def is_drivable(self):
		return (self.previousRightSensorValue <= self.drivableDistance or self.rightSensorValue <= self.drivableDistance) and (self.previousLeftSensorValue <= self.drivableDistance or self.leftSensorValue <= self.drivableDistance)
