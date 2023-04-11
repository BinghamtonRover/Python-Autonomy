from network import ProtoSocket, Device
from network.src.generated.Protobuf.autonomy_pb2 import *
from bin.demo3 import AutonomyProcess

process = None

class AutonomyServer(ProtoSocket): 
	def on_message(self, message, source):  # override 
		if (message.name == "AutonomyCommand"): 
			command = AutonomyCommand.FromString(message.data)
			if (command.enable): enable_autonomy()
			else: disable_autonomy()
		else: 
			print(f"Received unknown {message.name} from {source}")

	# def on_loop(self): print("Checking")

def enable_autonomy():
	global process
	process = AutonomyProcess()
	process.start()
	
def disable_autonomy():
	print("Closing autonomy")
	global process
	if process is None: return
	process.terminate()
	process = None
	

server = AutonomyServer(port=8003, device=Device.AUTONOMY)
server.listen()
