import threading

class ServerProcess(threading.Thread):
	def __init__(self, server): 
		super().__init__()
		self.keep_running = True
		self.server = server
		self.daemon = True

	def run(self):
		while True:
			if not self.server.keep_alive: break
			try: self.server.listen()
			except KeyboardInterrupt: break
			except OSError as error: 
				if error.errno in [10054, 101]: continue
				else: raise error

	def close(self): self.server.keep_alive = False
