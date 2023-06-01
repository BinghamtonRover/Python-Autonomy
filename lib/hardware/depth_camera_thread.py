import sys
import time
import threading
import cv2

from network import *
from network.generated import *

class DepthCameraThread(threading.Thread):
	def __init__(self, collection, test=False):
		print("[Info] Initializing Depth Camera...")
		super().__init__()
		self.keep_alive = True
		#if test or sys.platform != "linux":
		#	self.session = MockGps()
		#else: 
		#	self.session = gps.gps("localhost", "2947")
		self.collection = collection
		self.depth_frame = None
		self.color_frame = None
		self.init_realsense()
		self.read_frames()

	def close(self): 
		self.keep_alive = False

	# TODO: Remove in favor of directly accessing self.coordinates
	def read_depth_frame(self):
		return self.depth_frame
	
	def read_color_frame(self):
		return self.color_frame

    def set_orientation(self):
        self.collection.drive.set_camera_tilt(self.collection.imu.get_orientation()[0] + 90.0)

	def read_frames(self):
        frames = self.pipeline.wait_for_frames()
        self.depth_frame = frames.get_depth_frame()
        self.color_frame = frames.get_color_frame()
		self.collection.video.send_frame(frame=self.color_frame, name=CameraName.ROVER_FRONT)
		self.collection.video.send_frame(frame=cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET), name=CameraName.AUTONOMY_DEPTH)

	def run(self):
		while self.keep_alive:
            self.set_orientation()
			self.read_frames()
			
    def init_realsense(self):
        # Load proper settings
        self.load_high_density_settings()

        # Configure streams
        self.config = rs.config()
        self.config.enable_stream(rs.stream.depth, self.camera_width, self.camera_height, rs.format.z16, 30)
        self.config.enable_stream(rs.stream.color, self.camera_width, self.camera_height, rs.format.bgr8, 30)

        # Start streaming
        self.pipeline.start(self.config)

	    def _find_device_that_supports_advanced_mode(self) :
        ctx = rs.context()
        ds5_dev = rs.device()
        devices = ctx.query_devices()
        print("devices:")
        print(list(devices))
        for dev in devices:
            if dev.supports(rs.camera_info.product_id) and str(dev.get_info(rs.camera_info.product_id)) in DS5_PRODUCT_IDS:
                print(rs.camera_info.name)
               	if dev.supports(rs.camera_info.name):
                    print("Found device that supports advanced mode:", dev.get_info(rs.camera_info.name))
                return dev
        raise Exception("No device that supports advanced mode was found")

    def load_high_density_settings(self):
        dev = self._find_device_that_supports_advanced_mode()
        advnc_mode = rs.rs400_advanced_mode(dev)
        print("Advanced mode is", "enabled" if advnc_mode.is_enabled() else "disabled")
        while not advnc_mode.is_enabled():
            print("Trying to enable advanced mode...")
            advnc_mode.toggle_advanced_mode(True)
            # At this point the device will disconnect and re-connect.
            print("Sleeping for 5 seconds...")
            time.sleep(5)
            # The 'dev' object will become invalid and we need to initialize it again
            dev = find_device_that_supports_advanced_mode()
            advnc_mode = rs.rs400_advanced_mode(dev)
            print("Advanced mode is", "enabled" if advnc_mode.is_enabled() else "disabled")
        with open('high-density-camera.json') as j_file:
            json_dict = json.load(j_file)
            advnc_mode.load_json(json.dumps(json_dict))

    def clean_up(self):
        self.pipeline.stop()