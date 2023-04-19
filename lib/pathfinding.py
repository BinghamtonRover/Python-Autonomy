import sys
from queue import PriorityQueue
import math
import time
import threading
import gps_reader
import obstacle_avoidance
from imu import Imu

class Pathfinding:
    def __init__(self, gps_reader, imu_reader, camera, target_gps_coords):
        # create readers
        self.gps_reader = gps_reader GPSReader()
        self.imu_reader = imu_reader Imu()
        #self.camera = camera ObstacleDetectionCamera(2.4, 240, -0.3)

        # grid info
        self.gps_base = (0, 0)
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
        self.gps_base = self._read_gps()
        self.gps_goal = self._gps_to_grid(target_gps_coords) # gps_goal = ?? (read from somewhere else)
        goal_node = self._gps_to_grid(self.gps_goal)

        # visual processing data
        self.blocking_depth_threshold = 5
        self.camera_horizontal_fov = 87

    def pathfinding(self):
        # read data
        self._read_data()

        # calculate the path and target direction
        path = self._a_star(lambda a, b : (abs(b[0] - a[0]) + abs(b[1] - a[1])))
        dir = (self._get_direction(path)) * (180.0 / (math.pi))

        # output target direction (rotation needed to point in target direction)
        if dir < 0.0:
            dir += 360.0
        target_direction = dir - self.compass_direction
        if target_direction < 0.0:
            target_direction += 360.0
        
        # output target direction
        return target_direction

    def is_at_goal(self):
        return (self.current_position == self._gps_to_grid(self.target_gps_coords))

    def _read_data(self):
        # read gps, compass, and camera data
        self.current_position = self._gps_to_grid(self._read_gps())
        self.compass_direction = self._read_compass()
        self.camera_data = self._read_camera()
        self._update_blocked_areas()

    # read gps coordinates
    def _read_gps(self):
        return gps_reader.read_gps()

    # read compass direction
    def _read_compass(self):
        return imu_reader.get_orientation()[2]

    # read camera
    def _read_camera(self):
        return 24 * [-1.0]
        #return self.camera.get_distances(24)

    # convert gps coordinates to grid coordinates
    def _gps_to_grid(self, cords):
        x = round((cords[0] - self.gps_base[0]) / self.latitude_longitude_granularity)
        y = round((cords[1] - self.gps_base[1]) / self.latitude_longitude_granularity)
        return (x, y)

    # update areas that are blocked based on camera data
    def _update_blocked_areas(self):
        depth_data_length = float(len(self.camera_data))
        index = 0.0
        for depth in camera_data:
            if depth <= self.blocking_depth_threshold and depth != -1.0:
                offset_angle = ((self.camera_horizontal_fov / (2.0 * depth_data_length)) * ((2 * index) + 1)) - (self.camera_horizontal_fov / 2.0)
                exact_angle = (self.compass_direction + offset_angle) % 360.0
                blocked_x = round(self.current_position[0] + (depth * math.sin((180.0 / math.pi) * exact_angle)))
                blocked_y = round(self.current_position[1] + (depth * math.cos((180.0 / math.pi) * exact_angle)))
                if not (blocked_x == self.current_position[0] and blocked_y == self.current_position[1]) and not self._set_contains((blocked_x, blocked_y), self.is_blocked):
                    self.is_blocked.add(blocked_x, blocked_y)

    # take a path found from a-star and return a direction to move
    def _get_direction(self, path):
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
                return math.atan2(prev_node[1] - self.current_position[1], prev_node[0] - self.current_position[0])
            prev_node = node
        return math.atan2(goal_node[1] - self.current_position[1], goal_node[0] - self.current_position[0])

    # a star
    def _a_star(self, h_func):
        #start_time = time.time()
        open_queue = PriorityQueue()
        closed_nodes = set([])
        parent = {}
        g_func = {}

        open_queue.put((0, self.current_position))
        g_func[self.current_position] = 0
        goal_found = False
        while (not open_queue.empty() and not goal_found):
            self.current_position = open_queue.get()[1]
            if self._set_contains(self.current_position, closed_nodes):
                continue
            elif self.current_position == goal_node:
                goal_found = True
            else:
                g_val = g_func[self.current_position] + 1
                for adj_node in self._get_adjacent_nodes(self.current_position):
                    f_val = g_val + (h_func(adj_node, goal_node))
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
                            parent[adj_node] = self.current_position
                closed_nodes.add(self.current_position)
        
        if (not goal_found):
            print("No solution found")
            return None
        else:
            path = []
            parent_node = goal_node
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
        
    def _set_contains(self, val, set):
        return val in set

    def rotational_equality(self, a, b):
        return ((a - b) % 360.0 < 1.0)

    def location_equality(self, a, b):
        return (self._gps_to_grid(a) == self._gps_to_grid(b))