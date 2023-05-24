from network import *
from network.generated import *

import threading
import cv2

fps = 24

class AutonomyVideoServer(ProtoSocket):
	"""Responds to heartbeats and reports that all cameras are functional.

	Since the dashboard's video port may be anything, we use this class to "replace" the normal video
	program and wait for the dashboard to connect to us. Then, we can provide a [VideoClient] with the
	right port number for the dashboard.
	"""
	def __init__(self, port, collection): 
		super().__init__(port=port, device=Device.VIDEO)
		self.collection = collection
		self.quality = 70

	def close(self): 
		super().close()

	def on_connect(self, source): 
		super().on_connect(source)

	def on_disconnect(self): 
		super().on_disconnect()

	def send_frame(self, camera_id, frame, name):
		encoded, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, self.quality])
		details = CameraDetails(name=name, status=CameraStatus.CAMERA_ENABLED, fps=fps, quality=self.quality)
		message = VideoData(id=camera_id, details=details, frame=buffer.tobytes())
		self.send_message(message)

	def on_message(self, wrapper): 
		if wrapper.name == "VideoCommand": 
			# We're in a separate process from AutonomyProcess and VideoClient, so put this information in
			# the video client's queue, so it can retrieve it later. Naturally, then, no commands that 
			# modify the control flow will work, like FPS. That is by design, as those parameters are up
			# to the autonomy program.
			command = VideoCommand.FromString(wrapper.data)
			self.send_message(command)
			# For now, the only command we accept is quality, as that can save network bandwidth.
			# To simplify things, we only accept one quality parameter for both cameras.
			# It is now the responsibility of the VideoClient to read this value and compress accordingly
			self.quality = command.details.quality
