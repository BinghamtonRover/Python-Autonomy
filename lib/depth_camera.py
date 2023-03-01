import pyrealsense2 as rs
import bisect
from statistics import mean
import cv2
import numpy as np
import imutils

class DepthCamera:
    def __init__(self):
        # Create a context object. This object owns the handles to all connected realsense devices
        self.pipeline = rs.pipeline()

        # Configure streams
        self.config = rs.config()
        self.config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        self.config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

        # Start streaming
        self.pipeline.start(self.config)
        
        # cv2
        self.dictionary = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)
        self.parameters = cv2.aruco.DetectorParameters_create()
        
        self.minY = 140
        self.maxY = 280
        self.target_mins_total = 500.0
        self.zero_limit = 30000

    def get_distances(self, sections):
        frames = self.pipeline.wait_for_frames()
        depth = frames.get_depth_frame()
        
        if not depth:
            return []
        dists = []

        current_mins = []
        current_section = 0
        target_mins_per_section = int(self.target_mins_total / float(sections))
        zero_limit_per_section = int(self.zero_limit / float(sections))
        lower_data_trim = int(target_mins_per_section/2.0)
        num_zeroes = 0
        for x in range(640):
            for y in range(self.minY, self.maxY + 1):
                sect = int(float(x) / (640.0 / float(sections)))
                if sect != current_section:
                    if num_zeroes < zero_limit_per_section:
                        dists.append(mean(current_mins[int(len(current_mins)/2.0):int(len(current_mins)/1.2)]))
                    else:
                        dists.append(0.0)
                    current_mins = []
                    current_section = sect
                    num_zeroes = 0
                dist = 0.001 * depth.get_distance(x, y) #0.001 converts to meters (this actually isn't true)
                if dist == 0.0:
                    num_zeroes += 1
                else:
                    if len(current_mins) < target_mins_per_section:
                        bisect.insort(current_mins, dist)
                    elif dist < current_mins[target_mins_per_section - 1]:
                        bisect.insort(current_mins, dist)
        if num_zeroes < zero_limit_per_section:
            dists.append(mean(current_mins[int(len(current_mins)/2.0):int(len(current_mins)/1.2)]))
        else:
            dists.append(0.0)
        return dists
    
    def read_markers(self):
        # Get frame from camera
        realsense_frames = self.pipeline.wait_for_frames()
        color = realsense_frames.get_color_frame()
        frame = np.asanyarray(color.get_data())
        frame = imutils.resize(frame, width=1000)
        return self.detect_markers(frame)

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
        self.pipeline.stop()
