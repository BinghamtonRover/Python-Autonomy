import pyrealsense2 as rs
import bisect
from statistics import mean
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
    def get_distances(self, heights):
        # read depth frame
        frames = self.pipeline.wait_for_frames()
        depth = frames.get_depth_frame()

        if depth:
            # loop through, but only look at certain rows
            current_distances = []
            for i in range(64):
                current_distances.append([])
            all_distances = []
            for y in heights:
                dists = []
                for x in range(640):
                    dists.append(depth.get_distance(x, y))
                all_distances.append(dists)
            return all_distances

    def _unblocked_to_large(self, l):
        out = []
        for i in l:
            if i == -1.0:
                out.append(20.0)
            else:
                out.append(i)
        return out

    def _get_smaller_half(self, l):
        if len(l) == 0:
            return [10.0]
        med = np.percentile(l, 0.3)
        out = []
        for i in l:
            if i <= med and i != 0:
                out.append(i)
        if len(out) <= 10:
            return [0.0]
        return out

    def _safe_mean(self, l):
        if len(l) == 0:
            return 0.0
        return mean(l)

    def is_blocked(self):
        d = self.get_distances(64)
        if len(d) == 0:
            return False
        #print(mean(self._get_smaller_half(self._unblocked_to_large(d[20:44]))))
        #print(list(map(lambda a : int(a), d)))
        #return (mean(self._get_smaller_half(self._unblocked_to_large(d[20:44]))) < 1.5)
        return (self._safe_mean(self._unblocked_to_large(d[24:40])) < 1.3)

    def read_markers(self):
        # Get frame from camera
        realsense_frames = self.pipeline.wait_for_frames()
        color = realsense_frames.get_color_frame()
        depth = realsense_frames.get_depth_frame()
        frame = np.asanyarray(color.get_data())
        frame = imutils.resize(frame, width=1000)
        return self._detect_markers(frame, depth)

    def _detect_markers(self, frame, depth):
        corners, ids, rejected = cv2.aruco.detectMarkers(frame, self.dictionary, parameters = self.parameters)
        if len(corners):
            markers = []
            index = 0
            for x in ids:
                pos = self._get_marker_position(x, corners[index], frame, depth)
                markers.append((x[0], pos[0], pos[1], pos[2]))
                index += 1
            return markers
        return []

    def _get_marker_position(self, ids, corners, frame, depth):
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

            # Calculates distances to tag
            x_center = int(center[0] * (depth.get_width() / len(frame[0])))
            y_center = int(center[1] * (depth.get_height() / len(frame)))
            depth_vals = []
            for x in range(x_center - 2, x_center + 2, 1):
                for y in range(y_center - 2, y_center + 2, 1):
                    if x < depth.get_width() and y < depth.get_height():
                        d = depth.get_distance(x, y)
                        if d != 0.0:
                            depth_vals.append(d)
            if len(depth_vals) > 0:
                return (center[0], center[1], mean(depth_vals))
            return (center[0], center[1], -1)

    def clean_up(self):
        self.pipeline.stop()

