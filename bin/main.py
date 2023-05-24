from network import *
from lib.network import *

class Collection: 
	def __init__(self):
		self.video = AutonomyVideoServer(port=8002, collection=self)
		self.data = AutonomyServer(port=8004, collection=self)
		self.autonomy = AutonomyThread(collection=self)

if __name__ == "__main__":
	print("Starting program...")
	collection = Collection()

	data_server_process = ServerThread(collection.data)
	video_server_process = ServerThread(collection.video)

	data_server_process.start()
	video_server_process.start()

	try:
		while True: time.sleep(100)
	except (KeyboardInterrupt, SystemExit): pass
	finally: 
		print("Closing sockets...")
		data_server_process.close()
		video_server_process.close()
		collection.autonomy.close()
		video_server_process.join()
		data_server_process.join()
