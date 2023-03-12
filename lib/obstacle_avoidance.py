import pyrealsense2 as rs
import bisect
from statistics import mean
import cv2
import numpy as np
import imutils

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
        
        self.minY = 140
        self.maxY = 460
        self.cutoff_dist = cutoff_dist
        self.max_zeroes = max_zeroes
        self.block_height = 10
        self.min_slope = min_slope

    def get_distances(self, sections):
        frames = self.pipeline.wait_for_frames()
        depth = frames.get_depth_frame()
        block_width = int(self.camera_width / sections)
        
        if not depth:
            return []
        dists = []

        current_distances = []
        for horizontal_section in range(sections):
            already_appended = False
            previous_row_blocked = False
            previous_row_distance = -1.0
            horizontal_section_minimum =(horizontal_section * block_width)
            for vertical_section in range(int((self.maxY - self.minY) / self.block_height) - 1, -1, -1):
                vertical_section_minimum = (vertical_section * self.block_height) + self.minY
                section_values = []
                zeroes = 0
                cutoff_reached = False
                for y in range(vertical_section_minimum, vertical_section_minimum + self.block_height):
                    for x in range(horizontal_section_minimum, horizontal_section_minimum + block_width):
                        dist = depth.get_distance(x, y)
                        if dist == 0.0:
                            zeroes += 1
                        else:
                            section_values.append(dist)
                if zeroes >= self.max_zeroes and not cutoff_reached:
                    if previous_row_blocked:
                        current_distances.append(0.0)
                        already_appended = True
                        x = self.camera_width + 1
                        y = self.camera_height + 1
                        vertical_section = -1
                        break
                    previous_row_blocked = True
                elif previous_row_distance == -1:
                    row_dist = 0.0
                    if not len(section_values) == 0:
                        row_dist = mean(section_values)
                    previous_row_distance = row_dist
                    
                    #if horizontal_section == 4:
                    #    print("########")
                    #    print(horizontal_section_minimum)
                    #    print(horizontal_section_minimum + block_width)
                    #    print(row_dist)
                else:
                    previous_row_blocked = False
                    row_dist = 0.0                
                    if not len(section_values) == 0:
                        row_dist = mean(section_values)
                        
                    #if horizontal_section == 4:
                    #    print(row_dist)
                        
                    if row_dist > self.cutoff_dist:
                        cutoff_reached = True
                    elif previous_row_distance - row_dist > self.min_slope:
                        previous_row_distance = row_dist
                        continue
                    else:
                        already_appended = True
                        current_distances.append(row_dist)
                        x = self.camera_width + 1
                        y = self.camera_height + 1
                        vertical_section = -1
                        break
            if not already_appended and len(current_distances) < sections:
                current_distances.append(-1.0)
        return current_distances

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

