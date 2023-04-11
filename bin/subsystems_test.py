import time

from network import ProtoSocket, Device
from network.src.generated.Protobuf.drive_pb2 import DriveCommand
from lib.drive import Drive

socket = ProtoSocket(port=8000, device=Device.DASHBOARD, destination=("127.0.0.1", 8001))
drive = Drive(socket)

def drive_forward(): 
	drive.set_speeds(left=1.0, right=1.0)

def drive_backward(): 
	drive.set_speeds(left=-1.0, right=-1.0)

if __name__ == "__main__": 
	try: 
		drive.set_throttle(1.0)
		while True: 
			drive_forward()
			time.sleep(2)
			drive_backward()
			time.sleep(2)
	except KeyboardInterrupt: pass
	finally: 
		drive.set_throttle(0)
		socket.close()
