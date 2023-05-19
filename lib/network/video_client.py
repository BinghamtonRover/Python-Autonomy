import cv2

from network import *
from network.generated import *

class VideoClient(ProtoSocket):
	def send_frame(self, camera_id, frame, details):
		encoded, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, details.quality])
		message = VideoData(id=camera_id, details=details, frame=buffer.tobytes())
		self.send_message(message)
