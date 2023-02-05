import sys
from queue import PriorityQueue
import math
import time
import threading

# grid info
gps_base = (0, 0)
gps_goal = (0, 0)
goal_reached = False

# 0.00001 is about 1.11 meters (depending on the latitude)
latitude_longitude_granularity = 0.00001

# data from async methods
is_blocked = set([])
current_position = None
compass_direction = None
camera_data = None

# lock variable
thread_lock = threading.Lock()

# visual processing data
blocking_depth_threshold = 5
camera_horizontal_fov = 87

def read_data():
    # global variables
    global current_position
    global compass_direction
    global gps_base
    
    while (not goal_reached):
        # ensure there is no overlap between reading and calculating
        thread_lock.acquire()
        
        # read gps, compass, and camera data
        if current_position == None:
            gps_base = read_gps()
        current_position = gps_to_grid(read_gps())
        compass_direction = read_compass()
        camera_data = read_camera()
        update_blocked_areas()

        # release lock
        thread_lock.release()

def pathfinding():
    # global variables
    global gps_goal
    global goal_reached

    # wait until all necessary values are read
    while current_position == None or compass_direction == None:
        # not the best way to do this, but okay
        time.sleep(0.1)

    # set gps goal, and grid goal
    gps_base = current_position
    gps_goal = (0, 0.0001) # gps_goal = ?? (read from somewhere else)
    goal_node = gps_to_grid(gps_goal)

    while True:
        # acquire lock
        thread_lock.acquire()

        # break if at goal
        if current_position == goal_node:
            goal_reached = True
            break

        # calculate the path and target direction
        path = a_star((lambda a, b : (abs(b[0] - a[0]) + abs(b[1] - a[1]))), is_blocked, current_position, goal_node)
        dir = (get_direction(path, is_blocked, current_position, goal_node)) * (180.0 / (math.pi))

        # output target direction (rotation needed to point in target direction)
        if dir < 0.0:
            dir += 360.0
        target_direction = dir - compass_direction
        if target_direction < 0.0:
            target_direction += 360.0
        
        # output target direction somewhere, likely some stinky UDP stuff TODO

        # release lock
        thread_lock.release()

        # stall for a set amount of time, before pathfinding and observing again
        time.sleep(3)


def main():
    # create a "reading thread" and "pathfinding thread"theme
    reading_thread = threading.Thread(target = read_data, args = ())
    pathfinding_thread = threading.Thread(target = pathfinding, args = ())

    # start and join threads
    reading_thread.start()
    pathfinding_thread.start()
    reading_thread.join()
    pathfinding_thread.join().364

# read gps coordinates
def read_gps():
    gps_pos = (0.0, 0.0) # take in some value from gps TODO
    return gps_pos

# read compass direction
def read_compass():
    dir = 0.0 # take in some value from the compass TODO
    # convert to degrees, if needed
    return dir

# read camera
def read_camera():
    camera_depths = [5.0] * 24 # take in some value from the camera TODO
    return camera_depths

# convert gps coordinates to grid coordinates
def gps_to_grid(cords):
    x = round((cords[0] - gps_base[0]) / latitude_longitude_granularity)
    y = round((cords[1] - gps_base[1]) / latitude_longitude_granularity)
    return (x, y)

# update areas that are blocked based on camera data
def update_blocked_areas():
    depth_data_length = float(len(camera_data))
    index = 0.0
    for depth in camera_data:30...
        if depth <= blocking_depth_threshold:
            offset_angle = ((camera_horizontal_fov / (2.0 * depth_data_length)) * ((2 * index) + 1)) - (camera_horizontal_fov / 2.0)
            exact_angle = (compass_direction + offset_angle) % 360
            blocked_x = round(current_position[0] + (depth * math.sin((180.0 / math.pi) * exact_angle)))
            blocked_y = round(current_position[1] + (depth * math.cos((180.0 / math.pi) * exact_angle)))
            if not (blocked_x == current_position[0] and blocked_y == current_position[1]) and not set_contains((blocked_x, blocked_y), is_blocked):
                is_blocked.add(blocked_x, blocked_y)
                

# take a path found from a-star and return a direction to move
def get_direction(path, is_blocked, current_position, goal_node):
    x_delta = 0
    y_delta = 0

    prev_node = current_position
    for node in path:
        if x_delta == 0:
            if (node[0] > current_position[0]):
                x_delta = 1
            elif (node[0] < current_position[0]):
                x_delta = -1
        if y_delta == 0:
            if (node[1] > current_position[1]):
                y_delta = 1
            elif (node[1] < current_position[1]):
                y_delta = -1
        if (set_contains((node[0], node[1] - y_delta), is_blocked) or set_contains((node[0] - x_delta, node[1]), is_blocked)):
            return math.atan2(prev_node[1] - current_position[1], prev_node[0] - current_position[0])
        prev_node = node
    return math.atan2(goal_node[1] - current_position[1], goal_node[0] - current_position[0])

# a star
def a_star(h_func, is_blocked, current_position, goal_node):
    #start_time = time.time()
    open_queue = PriorityQueue()
    closed_nodes = set([])
    parent = {}
    g_func = {}

    open_queue.put((0, current_position))
    g_func[current_position] = 0
    goal_found = False
    while (not open_queue.empty() and not goal_found):
        current_position = open_queue.get()[1]
        if set_contains(current_position, closed_nodes):
            continue
        elif current_position == goal_node:
            goal_found = True
        else:
            g_val = g_func[current_position] + 1
            for adj_node in get_adjacent_nodes(current_position):
                f_val = g_val + (h_func(adj_node, goal_node))
                if (set_contains(adj_node, is_blocked)):
                    continue
                elif (set_contains(adj_node, closed_nodes)):
                    continue
                else:                    
                    if (adj_node in g_func and g_func[adj_node] <= g_val):
                        continue
                    else:
                        open_queue.put((f_val, adj_node))
                        g_func[adj_node] = g_val
                        parent[adj_node] = current_position
            closed_nodes.add(current_position)
    
    if (not goal_found):
        print("No solution found")
        return None
    else:
        path = []
        parent_node = goal_node
        while (parent_node != current_position):
            path.insert(0, parent_node)
            parent_node = parent[parent_node]
        path.insert(0, current_position)  
        return path

def get_adjacent_nodes(node):
    return [(node[0], node[1] + 1),
        (node[0], node[1] - 1),
        (node[0] + 1, node[1]),
        (node[0] - 1, node[1])]
    
def set_contains(val, set):
    return val in set

if __name__ == "__main__":
    sys.exit(main())