import time

from network import ProtoSocket, Device
from network.src.generated.Protobuf.drive_pb2 import DriveCommand

client = ProtoSocket(port=8000, device=Device.DASHBOARD, destination=("127.0.0.1", 8001))

def drive_forward(): 
	client.send_message(DriveCommand(set_left=True, left=1, set_right=True, right=1, set_throttle=True, throttle=1))

def drive_backward(): 
	client.send_message(DriveCommand(set_left=True, left=-1, set_right=True, right=-1, set_throttle=True, throttle=1))

def stop(): 
	client.send_message(DriveCommand(set_throttle=True, throttle=0))

if __name__ == "__main__": 
	try: 
		while True: 
			drive_forward()
			time.sleep(2)
			drive_backward()
			time.sleep(2)
	except KeyboardInterrupt: pass
	finally: 
		stop()
		client.close()
