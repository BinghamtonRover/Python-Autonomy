import pyrealsense2 as rs
import bisect
from statistics import mean
import cv2
import numpy as np
import imutils
import json

class MockRealSense:
    def __init__(self): 
        print("[Warning] Using mock realsense")

    def start(self, *args): pass
    def stop(self, *args): pass

DS5_PRODUCT_IDS = ["0AD1", "0AD2", "0AD3", "0AD4", "0AD5", "0AF6", "0AFE", "0AFF", "0B00", "0B01", "0B03", "0B07","0B3A"]

class ObstacleDetectionCamera:
    def __init__(self, cutoff_dist, max_zeroes, min_slope, test=False, depth_camera_thread):
        print("[Info] Initializing Obstacle Detection Camera")
        self.test = test
        self.camera_width = 640
        self.camera_height = 480
        # ((maxY - minY) % block_height) needs to equal 0
        self.minY = 140                  # lower frame cutoff
        self.maxY = 480                 # upper frame cutoff
        self.cutoff_dist = cutoff_dist  # (depth cutoff) maximum distance the camera will analyze
        self.max_zeroes = max_zeroes    # max number of zeroes per section
        self.block_height = 15           # height of sections the screen is separated into
        #self.a = 0.055                  # "a" value used in function to calculate maximum slope between blocks in frame, I found this to be about 0.05 through some tests
        self.a = 0.01
        self.fixed_min_slope = -0.017   # idk maybe try this I feel like shit but the thing above has a bug :skull:
        # self.dictionary = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)
        # self.parameters = cv2.aruco.DetectorParameters_create()
        # Create a context object. This object owns the handles to all connected realsense devices
        self.dashboard = dashboard
        #if test: 
        #    self.pipeline = MockRealSense()
        #else:
        #    self.pipeline = rs.pipeline()
        #    self.init_realsense()
        self.depth_camera_thread = depth_camera_thread
        
    def is_blocked(self):
        if self.test: return False
        else: return (self._is_blocked() and self._is_blocked() and self._is_blocked())

    def _is_blocked(self):
        dists = self._get_distances(20)
        consecutive_blocked = 0
        for d in dists[5:15]:
            if d != -1.0 or d >= 1.1:
                consecutive_blocked += 1
                if consecutive_blocked == 5:
                    return True
            elif d != 0.0:
                consecutive_blocked = 0
        return False

    def get_distances(self, sections):
        l = []
        for i in range(5):
            l.append(self._get_distances(20))
        dists = []
        for i in range(len(l[i])):
            row_dists = []
            zeroes = 0
            for j in range(len(l)):
                x = l[j][i]
                if x == 0.0:
                    zeroes += 1
                elif x != -1.0:
                    row_dists.append(l[j][i])
            if zeroes >= 3:
                dists.append(0.0)
            elif len(row_dists) <= 2:
                dists.append(-1.0)
            else:
                dists.append(mean(row_dists))
        #print(dists)
        return dists

    # returns an array of distance to an object on each horizontal section of the frame, with -1.0 being unblocked
    # [sections] is the amount of columns to split the screen into
    def _get_distances(self, sections:int) -> [int]:
        # read depth frame
        depth = self.depth_camera_thread.get_depth_frame()
        if not depth:
            return []

        # width of sections to be analyzed
        block_width = int(self.camera_width / sections)

        # return value
        current_distances = []

        # "sweep" up through the block, so choose a horizontal section and then step up the vertical sections
        for horizontal_section in range(sections):
            already_appended = False
            previous_row_zeroed = False
            cutoff_reached = False
            previous_row_distance = -1.0
            horizontal_section_minimum = (horizontal_section * block_width)
            sum_of_first_two_vertical_sections = 0.0

            for vertical_section in range(int((self.maxY - self.minY) / self.block_height) - 1, -1, -1):
                vertical_section_minimum = (vertical_section * self.block_height) + self.minY

                # read data from a given section
                section_info = self._read_section(depth, vertical_section_minimum, horizontal_section_minimum, block_width)
                zeroes = section_info[0]
                section_values = section_info[1]

                # if we see too many zeroes before hitting the cutoff distance, then this section is not useful
                if zeroes >= self.max_zeroes and not cutoff_reached:
                    # if this is the second zero block we saw, then the entire horizontal section does not have enough data, append 0 and go to next
                    if previous_row_zeroed:
                        current_distances.append(0.0)
                        already_appended = True
                        previous_row_zeroed = False
                        break
                    else:
                        previous_row_zeroed = True

                # we cannot check slope for first row (previous_row_distance is only -1 in first loop)
                elif previous_row_distance == -1:
                    row_dist = self._safe_mean(section_values)
                    previous_row_distance = row_dist

                # we cannot check slope for second row, as we still need to collect some data
                elif vertical_section == int((self.maxY - self.minY) / self.block_height) - 2:
                    row_dist = self._safe_mean(section_values)

                    # calculate "sum of first two vertical sections", which is used in the slope formula (we cannot use a row if it is "0.0")
                    sum_of_first_two_vertical_sections = previous_row_distance + row_dist
                    previous_row_distance = row_dist

                # check if slope between section of frames is too steep
                else:
                    previous_row_zeroed = False
                    row_dist = self._safe_mean(section_values)

                    # don't check slope for first two vertical sections, we need these sections to calculate a value in or slope formula
                    if vertical_section >= ((self.maxY - self.minY) / self.block_height) - 2:
                        sum_of_first_two_vertical_sections += row_dist
                    else:
                        # calculate min slope based on regression formula I found
                        b = (sum_of_first_two_vertical_sections) + 1.0
                        min_slope = - (self.a / ((self.a + b) * (self.a + b)))

                        # don't worry past the cutoff distance
                        if row_dist > self.cutoff_dist:
                            cutoff_reached = True
                        # check if slope indicates there is an obstacle (undrivable terrain)
                        elif self.fixed_min_slope != None and previous_row_distance - row_dist < self.fixed_min_slope:
                            previous_row_distance = row_dist
                            continue
                        elif self.fixed_min_slope == None and previous_row_distance - row_dist < min_slope:
                            previous_row_distance = row_dist
                            continue
                        else:
                            already_appended = True
                            current_distances.append(row_dist)
                            break

            # if we reach this point an we have not already appended a value, then the row is unblocked
            if not already_appended:
                current_distances.append(-1.0)

        # return an array of the distance to an "obstacle" in each horizontal section
        return current_distances

    # calculate mean, if empty return 0.0
    def _safe_mean(self, section_values):
        if len(section_values) == 0:
            return 0.0
        else:
            return mean(section_values)

    # read section of frame
    def _read_section(self, depth, minY, minX, block_width):
        section_values = []
        zeroes = 0
        for y in range(minY, minY + self.block_height, 2):
            for x in range(minX, minX + block_width, 3):
                dist = depth.get_distance(x, y)
                if dist == 0.0:
                    zeroes += 1
                else:
                    section_values.append(dist)
        return (zeroes, section_values)

    def read_markers(self):
        # Get frame from camera
        color = self.depth_camera_thread.get_color_frame()
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

    def close(self): 
        self.clean_up()
