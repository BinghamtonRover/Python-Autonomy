import sys
from queue import PriorityQueue
import math
import time
import threading
import statistics
from lib.gps_reader import GPSReader
from lib.obstacle_avoidance import ObstacleDetectionCamera
from lib.imu.imu import Imu

class Pathfinding:
    def __init__(self, gps_reader, imu_reader, camera, target_gps_coords):
        # create readers
        self.gps_reader = gps_reader
        self.imu_reader = imu_reader
        self.camera = camera #ObstacleDetectionCamera(2.4, 240, -0.3)

        # grid info
        self.gps_base = target_gps_coords
        self.gps_goal = (0, 0)
        self.goal_reached = False

        # 0.00001 is about 1.11 meters (depending on the latitude)
        self.latitude_longitude_granularity = 0.00001

        # data from async methods
        self.is_blocked = set([])
        self.current_position = None
        self.compass_direction = None
        self.camera_data = None
        
        # set gps goal, and grid goal
        self.gps_goal = self._gps_to_grid(target_gps_coords) # gps_goal = ?? (read from somewhere else)
        goal_node = self._gps_to_grid(self.gps_goal)
        self.target_gps_coords = target_gps_coords

        # visual processing data
        self.camera_horizontal_fov = 87

    def _put_behind(self):
        if self.compass_direction < 45.0 or self.compass_direction > 315.0:
            self.current_position = (self.current_position[0] - latitude_longitude_granularity, self.current_position[1])
        elif self.compass_direction < 135.0:
            self.current_position = (self.current_position[0], self.current_position[1] + latitude_longitude_granularity)
        elif self.compass_direction < 225.0:
            self.current_position = (self.current_position[0] + latitude_longitude_granularity, self.current_position[1])
        else:
            self.current_position = (self.current_position[0], self.current_position[1] + latitude_longitude_granularity)

    def pathfinding(self):
        # read data
        self._read_data()
        while (self._set_contains(self._gps_to_grid(self.current_position), self.is_blocked)):
            self._put_behind()

        # calculate the path and target direction
        path = self._a_star(lambda a, b : (abs(b[0] - a[0]) + abs(b[1] - a[1])))
        target = self.get_target_node(path)
        # print(path)
        print(self.current_position)
        print(self.is_blocked)
        
        # output target direction and target location
        return target

    def is_at_goal(self):
        target_node = self._gps_to_grid(self.target_gps_coords)
        adj = self._get_adjacent_nodes_with_corners(target_node)
        adj.append(target_node)
        return self.current_position in adj

    def _read_data(self):
        # read gps, compass, and camera data
        self.current_position = self._gps_to_grid(self.read_gps())
        self.compass_direction = self._read_compass()
        self.camera_data = self._read_camera()
        self._update_blocked_areas()

    # read gps coordinates
    def read_gps(self):
        return self.gps_reader.read_gps()
        gps_vals = []
        gps_reading = self.gps_reader.read_gps()
        while len(gps_vals) < 20:
            if gps_reading not in gps_vals:
                gps_vals.append(gps_reading)
            gps_reading = self.gps_reader.read_gps()
        return (statistics.mean(map(lambda a : a[0], gps_vals)), statistics.mean(map(lambda a : a[1], gps_vals)))

    # read compass direction
    def _read_compass(self):
        return self.imu_reader.get_orientation()[2]

    # read camera
    def _read_camera(self):
        #return 24 * [-1.0]
        return self.camera.get_distances(20)

    # convert gps coordinates to grid coordinates
    def _gps_to_grid(self, cords):
        x = round((cords[0] - self.gps_base[0]) / self.latitude_longitude_granularity)
        y = round((cords[1] - self.gps_base[1]) / self.latitude_longitude_granularity)
        return (x, y)
    def _grid_to_gps(self, cords):
        x = (cords[0] * self.latitude_longitude_granularity) + self.gps_base[0]
        y = (cords[1] * self.latitude_longitude_granularity) + self.gps_base[1]
        return (x, y)

    # update areas that are blocked based on camera data by computing the coordinates where obstacles are located
    def _update_blocked_areas(self):
        depth_data_length = float(len(self.camera_data))
        index = 2.0
        for depth in self.camera_data[2:-2]:
            if depth != -1.0 and depth != 0.0 and self.camera_data[int(index) - 1] != -1.0 and self.camera_data[int(index) + 1] != -1.0:
                center_angle = ((self.camera_horizontal_fov / (2.0 * depth_data_length)) * ((2.0 * index) + 1)) - (self.camera_horizontal_fov / 2.0)
                angle1 = (center_angle + (self.camera_horizontal_fov / (2.0 * depth_data_length)) + self.compass_direction) % 360.0
                angle2 = (center_angle - (self.camera_horizontal_fov / (2.0 * depth_data_length)) + self.compass_direction) % 360.0
                point_dist = depth / (math.cos(abs(center_angle - angle1) * (math.pi / 180.0)))
                angle1 *= -(math.pi / 180.0)
                angle2 *= -(math.pi / 180.0)
                point1 = (self.current_position[0] + point_dist * math.cos(angle1), self.current_position[1] + point_dist * math.sin(angle1))
                point2 = (self.current_position[0] + point_dist * math.cos(angle2), self.current_position[1] + point_dist * math.sin(angle2))
                to_be_blocked = self._bresenhams_line_floating_point(point1, point2)
                for p in to_be_blocked:
                    self.is_blocked.add(p)
            index += 1

    # take a path found from a-star and return the target node in gps cords
    def get_target_node(self, path):
        x_delta = 0
        y_delta = 0
        prev_node = self.current_position
        for node in path:
            if x_delta == 0:
                if (node[0] > self.current_position[0]):
                    x_delta = 1
                elif (node[0] < self.current_position[0]):
                    x_delta = -1
            if y_delta == 0:
                if (node[1] > self.current_position[1]):
                    y_delta = 1
                elif (node[1] < self.current_position[1]):
                    y_delta = -1
            if (self._set_contains((node[0], node[1] - y_delta), self.is_blocked) or self._set_contains((node[0] - x_delta, node[1]), self.is_blocked)):
                return self._grid_to_gps(prev_node)
            prev_node = node
        return self._grid_to_gps(self.gps_goal)

    # take a target position and current position and calculate the direction to reach the target direction
    def get_direction(self, current_position, target):
        return (math.atan2(current_position[1] - target[1], -current_position[0] + target[0]) * (180.0 / math.pi)) % 360.0

    # a star (explanation here: https://www.geeksforgeeks.org/a-search-algorithm/)
    def _a_star(self, h_func):
        open_queue = PriorityQueue()
        closed_nodes = set([])
        parent = {}
        g_func = {}
        current_node = self.current_position

        open_queue.put((0, current_node))
        g_func[current_node] = 0
        goal_found = False
        while (not open_queue.empty() and not goal_found):
            current_node = open_queue.get()[1]
            if self._set_contains(current_node, closed_nodes):
                continue
            elif current_node == self.gps_goal:
                goal_found = True
            else:
                g_val = g_func[current_node] + 1
                for adj_node in self._get_adjacent_nodes(current_node):
                    f_val = g_val + (h_func(adj_node, self.gps_goal))
                    if (self._set_contains(adj_node, self.is_blocked)):
                        continue
                    elif (self._set_contains(adj_node, closed_nodes)):
                        continue
                    else:
                        if (adj_node in g_func and g_func[adj_node] <= g_val):
                            continue
                        else:
                            open_queue.put((f_val, adj_node))
                            g_func[adj_node] = g_val
                            parent[adj_node] = current_node
                closed_nodes.add(current_node)

        if (not goal_found):
            print("No solution found")
            return None
        else:
            path = []
            parent_node = self.gps_goal
            while (parent_node != self.current_position):
                path.insert(0, parent_node)
                parent_node = parent[parent_node]
            path.insert(0, self.current_position)
            return path

    def _get_adjacent_nodes(self, node):
        return [(node[0], node[1] + 1),
            (node[0], node[1] - 1),
            (node[0] + 1, node[1]),
            (node[0] - 1, node[1])]

    def _get_adjacent_nodes_with_corners(self, node):
        return [(node[0], node[1] + 1),
            (node[0], node[1] - 1),
            (node[0] + 1, node[1]),
            (node[0] - 1, node[1]),
            (node[0] + 1, node[1] + 1),
            (node[0] + 1, node[1] - 1),
            (node[0] - 1, node[1] + 1),
            (node[0] - 1, node[1] - 1)]

    def _set_contains(self, val, set):
        return val in set

    # given two points, create a continuous line of discrete points (integer pairs) from start to end
    def _bresenhams_line_floating_point(self, start, end):
        if start == end:
            return [(math.floor(start[0]), math.floor(start[1]))]
        line = []
        difX = end[0] - start[0]
        difY = end[1] - start[1]
        dist = abs(difX) + abs(difY)
        dx = difX / dist
        dy = difY / dist
        for i in range(0, math.ceil(dist) + 1):
            x = math.floor(start[0] + dx * i)
            y = math.floor(start[1] + dy * i)
            line.append((x, y))
        return list(dict.fromkeys(line))

    def rotational_equality(self, a, b):
        return ((a - b) % 360.0 < 3.0)

    def location_equality(self, a, b):
        return (self._gps_to_grid(a) == self._gps_to_grid(b))
