from networking import ProtoServer
from networking.generated.Protobuf.autonomy_pb2 import *
from bin.demo3 import AutonomyProcess

process = None

class AutonomyServer(ProtoServer): 
	def on_message(self, message, source): 
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
	

server = AutonomyServer(port=8006)
server.start()
