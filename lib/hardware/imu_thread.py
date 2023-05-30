import serial
import threading
import sys
import time

from .osc_decoder import decode
from network.generated import Orientation, RoverPosition

IMU_SERIAL_PORT = "COM25"

class MockImu:
	def __init__(self):
		print("[Warning] Using mock IMU")
		self.in_waiting = 0

	def read(self, *args, **kwargs): return bytearray(b'#bundle\x00\xe8\x19v\x08_\x08\xe0\x00\x00\x00\x00\x1c/euler\x00\x00,fff\x00\x00\x00\x00?D\xc2"@F\x01&B\xc5\x1a\xba\xc0#bundle\x00\xe8\x19v\x08x8\xb8\x00\x00\x00\x00\x1c/euler\x00\x00,fff\x00\x00\x00\x00?D\xc6\x07@D:\x0eB\xc5\x05\xbd\xc0')
	def close(self): pass

class ImuThread(threading.Thread):
	def __init__(self, collection, test=False):
		print("[Info] Initializing IMU thread...")
		super().__init__()
		self.collection = collection
		self.keep_alive = True
		self.orientation = Orientation()
		if test or sys.platform != "linux": 
			self.device = MockImu()
		else: 
			self.device = serial.Serial(IMU_SERIAL_PORT, 115200)

	def close(self): 
		self.keep_alive = False
		self.device.close()

	# TODO: Remove in favor of directly accessing self.orientation
	def get_orientation(self): 
		return (self.orientation.x, self.orientation.y, self.orientation.z)

	def run(self): 
		while self.keep_alive: 
			result = self.get_message()
			if not result: continue
			result = result[0]
			# TODO: Translate this into an [Orientation]
			name = result[1]
			if name != "/euler": continue
			self.orientation = Orientation(x=float(result[2]), y=float(result[3]), z=float(result[4]))
			message = RoverPosition(orientation=self.orientation)
			self.collection.dashboard.send_message(message)
			time.sleep(0.5)

	def get_message(self): 
		"""Reads bytes until "#bundle" and sends the result to osc_decoder.

		If the result is a failure or an error, simply read until the next 
		"#bundle" and try again. If 4 whole packets go by without success,
		we must have hit some unknown error and it's safer to fail.
		"""
		buffer = bytearray()
		i = 0
		while self.keep_alive: 
			data = self.device.read(size=self.device.in_waiting)
			# bundles must start with '#' (ASCII 35)
			if not data or data[0] != 35: continue  
			if i == 4: return None  # some unknown failure
			i += 1
			for index, b in enumerate(data): buffer.append(b)
			try: 
				result = decode(bytes(buffer))
				if result: return result
			except IndexError: pass
