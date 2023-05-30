import pyrealsense2 as rs
import bisect
from statistics import mean
from statistics import median
import cv2
import numpy as np
import imutils
import time

class ObstacleDetectionCamera:
    def __init__(self, cutoff_dist, max_zeroes, min_slope):
        # Create a context object. This object owns the handles to all connected realsense devices
        self.pipeline = rs.pipeline()

        # Configure streams
        self.camera_width = 640
        self.camera_height = 480
        self.config = rs.config()
        self.config.enable_stream(rs.stream.depth, self.camera_width, self.camera_height, rs.format.z16, 30)
        self.config.enable_stream(rs.stream.color, self.camera_width, self.camera_height, rs.format.bgr8, 30)

        # Start streaming
        self.pipeline.start(self.config)

        # cv2
        self.dictionary = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)
        self.parameters = cv2.aruco.DetectorParameters_create()

        self.minY = 140                 # lower frame cutoff
        self.maxY = 460                 # upper frame cutoff

    # returns an array of distance to an object on each horizontal section of the frame, with -1.0 being unblocked
    def get_distances(self, y_list):
        # read depth frame
        frames = self.pipeline.wait_for_frames()
        depth = frames.get_depth_frame()

        if depth:
            # loop through, but only look at certain rows
            current_distances = []
            for i in range(64):
                current_distances.append([])
            for x in range(640):
                for y in y_list:
                    dist = depth.get_distance(x, y)
                    if dist > 0:
                        l = current_distances[x//10]
                        l.append(dist)
                        current_distances[x//10] = l
            out = []
            for i in current_distances:
                if len(i) == 0:
                    out.append(0.0)
                else:
                    m = mean(i)
                    if m <= 5:
                        out.append(m)
                    else:
                        out.append(-1.0)
            return out
        else:
            return []

    def _unblocked_to_large(self, l):
        out = []
        for i in l:
            if i == -1.0:
                out.append(20.0)
            elif i != 0.0:
                out.append(i)
        return out

    def _get_smaller_half(self, l):
        med = median(l)
        out = []
        for i in l:
            if i <= med and i != 0:
                out.append(i)
        if len(out) == 0:
            return [0]
        print(out)
        return out

    def is_blocked(self):
        d = self.get_distances(64)
        if len(d) == 0:
            return False
        #print(mean(self._get_smaller_half(self._unblocked_to_large(d[20:44]))))
        return (mean(self._get_smaller_half(self._unblocked_to_large(d[20:44]))) < 0.8)

    def read_markers(self):
        # Get frame from camera
        realsense_frames = self.pipeline.wait_for_frames()
        color = realsense_frames.get_color_frame()
        frame = np.asanyarray(color.get_data())
        frame = imutils.resize(frame, width=1000)
        return self._detect_markers(frame)

    def _detect_markers(self, frame):
        corners, ids, rejected = cv2.aruco.detectMarkers(frame, self.dictionary, parameters = self.parameters)
        if len(corners):
            markers = []
            index = 0
            for x in ids:
                center = self._get_marker_position(x, corners[index])
                markers.append((x[0], center[0], center[1]))
                index += 1
            return markers
        return []

    def _get_marker_position(self, ids, corners):
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

