from network import *
from network.generated import *

class AutonomyServer(ProtoSocket): 
	def __init__(self, port, collection): 
		super().__init__(port=port, device=Device.AUTONOMY)
		self.collection = collection

	def on_disconnect(self): 
		super().on_disconnect()
		print("Autonomy server disconnected")
		self.disable_autonomy()

	def update_settings(self, settings): 
		super().update_settings(settings)
		if settings.status in [RoverStatus.IDLE, RoverStatus.MANUAL]: 
			self.disable_autonomy()
		elif settings.status == RoverStatus.AUTONOMOUS: 
			print("Autonomy enabled")
			pass  # don't do anything until AutonomyCommand is received

	def on_message(self, wrapper): 
		if wrapper.name == "AutonomyCommand": 
			settings = UpdateSetting.FromString(self.settings)
			if settings.status != RoverStatus.AUTONOMOUS: 
				print("Ignoring AutonomyCommands until we are in autonomous mode")
				return
			command = AutonomyCommand.FromString(wrapper.data)
			self.send_message(command)
			print(f"Received autonomy command: {command}")
			self.enable_autonomy(command)

	def enable_autonomy(self, command): 
		self.disable_autonomy()
		self.collection.autonomy.startTask(command)

	def disable_autonomy(self): 
		self.collection.autonomy.stopTask()

	def send_message(self, message):
		if self.is_connected(): super().send_message(message)
