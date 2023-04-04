import sys
sys.path.append("/home/pi/.local/lib/python3.9/site-packages")
from cgitb import html
from time import time
import cv2
import imutils
from imutils.video import VideoStream
import time
import math

class Marker:
    def __init__(self):
        self.dictionary = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)
        self.parameters = cv2.aruco.DetectorParameters_create()
        # usb camera
        #self.vid_stream = VideoStream(src=0).start()
        # realsense camera
        self.vid_stream = VideoStream(src=4).start()
        self.marker_dict = {
            0: "Start",
            1: "Post 1",
            2: "Post 2",
            3: "Post 3",
            4: "Gate Left",
            5: "Gate Right"
        }

    def detect_markers(self, frame):
        corners, ids, rejected = cv2.aruco.detectMarkers(frame, self.dictionary, parameters = self.parameters)
        if len(corners):
            markers = []
            index = 0
            for x in ids:
                center = self.get_marker_position(x, corners[index])
                markers.append((x[0], center[0], center[1]))
                index += 1
            return markers
        return []

    # Analyze frames from video stream
    def read_markers(self):
        # Get frame from camera
        frame = self.vid_stream.read()
        frame = imutils.resize(frame, width=1000)
        return self.detect_markers(frame)

    def get_marker_position(self, ids, corners):
        # If we found an ARUCO code
        for (markerCorner, markerID) in zip(corners, ids):
            corners = markerCorner.reshape((4,2))
            (topLeft, topRight, bottomLeft, bottomRight) = corners

            # Get corners of the code
            topLeft = (int(topLeft[0]), int(topLeft[1]))
            topRight = (int(topRight[0]), int(topRight[1]))
            bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
            bottomRight = (int(bottomRight[0]), int(bottomRight[1]))

            # Calculates center
            center = (int((topLeft[0] + bottomLeft[0]) / 2), int((topLeft[1] + bottomLeft[1]) / 2))
            return center
                

    def clean_up(self):
        self.vid_stream.stop()