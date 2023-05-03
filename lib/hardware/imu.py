from osc_decoder import decode
import serial
import time

s = serial.Serial("COM15", 115200)

def get_message(): 
	"""Reads bytes until "#bundle" and sends the result to osc_decoder.

	If the result is a failure or an error, simply read until the next 
	"#bundle" and try again. If 4 whole packets go by without success,
	we must have hit some unknown error and it's safer to fail.
	"""
	buffer = bytearray()
	i = 0
	while True: 
		data = s.read(size=s.in_waiting)
		# bundles must start with '#' (ASCII 35)
		if not data or data[0] != 35: continue  
		if i == 4: return None  # some unknown failure
		i += 1
		for index, b in enumerate(data): buffer.append(b)
		try: 
			result = decode(bytes(buffer))
			if result: return result
		except IndexError: pass

while True: 
	result = get_message()
	if not result: continue
	print(result)
