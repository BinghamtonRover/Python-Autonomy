from lib.pathfinding import Pathfinding
from lib.imu.imu import Imu
from lib.gps_reader import GPSReader
from lib.hardware.temp_tank_drive import Drive
#from lib.drive import Drive
from lib.obstacle_avoidance import ObstacleDetectionCamera
from lib.ultrasonic import Ultrasonic
#from network import ProtoSocket, Device
import time
import math

def main2(drive, gps, imu, camera, ultrasonic):
    # setup
    drive.set_speeds(0.0, 0.0)
    speed1 = 0.9
    print("starting")
    time.sleep(1.0)
    while gps.read_gps()[0] == 0:
        pass
    print("gps ready")
    while imu.get_orientation()[2] == 0:
        pass
    print("imu ready")
    pathfinding = Pathfinding(gps, imu, camera, (42.08740, -75.96750))
    # the camera gets mad if it doesn't get to think ahead of time >:(
    camera.get_distances(20)
    time.sleep(3.0)

    pathfind_to_find_marker(drive, gps, imu, camera, ultrasonic, pathfinding)

    done = False
    while not done:
        info = get_second_marker_info(camera.read_markers(), -1)
        if len(info) != 0:
            if info[1] > 330:
                drive.set_speeds(-0.7, 0.7)
            elif info[1] < 310:
                drive.set_speeds(0.7, -0.7)
            elif info[3] > 1.5:
                drive.set_speeds(0.8, 0.8)
            else:
                done = True
        else:
            drive.set_speeds(0.0, 0.0)
    drive.set_speeds(0.0, 0.0)
    print("done")

def pathfind_to_find_marker(drive, gps, imu, camera, ultrasonic, pathfinding):
    speed1 = 0.9
    # go to gps location
    while (not pathfinding.is_at_goal() and len(camera.read_markers()) == 0):
        print("running pathfinding")
        #print(imu.get_orientation()[2] % 360.0)
        #print(gps.read_gps())
        target_cords = pathfinding.pathfinding()
        current_direction = imu.get_orientation()[2] % 360.0
        start_point = gps.read_gps()
        target_direction = pathfinding.get_direction(start_point, target_cords)
        #print(target_direction)
        while not pathfinding.rotational_equality(target_direction, current_direction) and len(camera.read_markers()) == 0:
            adjust_to_face_target_direction(drive, target_direction, current_direction)
            current_direction = imu.get_orientation()[2] % 360.0
        drive.set_speeds(speed1, speed1)
        gps_pos = gps.read_gps()
        while not reached_point(start_point, target_cords, gps_pos) and not ultrasonic.is_blocked() and len(camera.read_markers()) == 0:
            print("us + td")
            print(ultrasonic.get_distance())
            print(target_direction)
            #print(math.pow(target_cords[0] - gps_pos[0], 2) + math.pow(target_cords[1] - gps_pos[1], 2))
            gps_pos = gps.read_gps()
            target_direction = pathfinding.get_direction(gps_pos, target_cords)
            current_direction = imu.get_orientation()[2] % 360.0
            adjust_while_moving_to_target(drive, target_direction, current_direction, 0.9, 0.4)
        print(ultrasonic.get_distance())
        if ultrasonic.is_blocked():
            drive.set_speeds(-0.9, -0.9)
            time.sleep(1.0)
        drive.set_speeds(0.0, 0.0)
    drive.set_speeds(0.0, 0.0)
    print("done!")

def main(drive, gps, imu, camera, ultrasonic):
    # setup
    drive.set_speeds(0.0, 0.0)
    speed1 = 0.9
    print("starting")
    time.sleep(1.0)
    while gps.read_gps()[0] == 0:
        pass
    print("gps ready")
    while imu.get_orientation()[2] == 0:
        pass
    print("imu ready")
    pathfinding = Pathfinding(gps, imu, camera, (42.08740, -75.96750))
    # the camera gets mad if it doesn't get to think ahead of time >:(
    camera.get_distances(20)
    time.sleep(3.0)

    # go to gps location
    while (not pathfinding.is_at_goal()):
        print("running pathfinding")
        #print(imu.get_orientation()[2] % 360.0)
        #print(gps.read_gps())
        target_cords = pathfinding.pathfinding()
        current_direction = imu.get_orientation()[2] % 360.0
        start_point = gps.read_gps()
        target_direction = pathfinding.get_direction(start_point, target_cords)
        #print(target_direction)
        while not pathfinding.rotational_equality(target_direction, current_direction):
            adjust_to_face_target_direction(drive, target_direction, current_direction)
            current_direction = imu.get_orientation()[2] % 360.0
        drive.set_speeds(speed1, speed1)
        gps_pos = gps.read_gps()
        while not reached_point(start_point, target_cords, gps_pos) and not ultrasonic.is_blocked():
            print("us + td")
            print(ultrasonic.get_distance())
            print(target_direction)
            #print(math.pow(target_cords[0] - gps_pos[0], 2) + math.pow(target_cords[1] - gps_pos[1], 2))
            gps_pos = gps.read_gps()
            target_direction = pathfinding.get_direction(gps_pos, target_cords)
            current_direction = imu.get_orientation()[2] % 360.0
            adjust_while_moving_to_target(drive, target_direction, current_direction, 0.9, 0.4)
        print(ultrasonic.get_distance())
        #drive.set_speeds(-0.9, -0.9)
        #time.sleep(1.0)
        drive.set_speeds(0.0, 0.0)
    drive.set_speeds(0.0, 0.0)
    print("done!")

def get_second_marker_info(camera_info, first_id):
    for i in markers:
        if i[0] != first_id:
            return i
    return []

def contains_second_marker(markers, first_id):
    for i in markers:
        if i[0] != first_id:
            return True
    return False

def drive_spiral(drive, current_rotation, current_position, origin, radius):
    rotation_vector = (-(current_position[1] - origin[1]), current_position[0] - origin[0])
    current_radius = math.sqrt(math.pow(rotation_vector[0], 2) + math.pow(rotation_vector[1], 2))
    target_direction = (math.atan2(-rotation_vector[1], rotation_vector[0]) * (180.0 / math.pi)) % 360.0
    error = 0.1
    if current_radius >= radius - error and current_radius <= radius + error:
        adjust_while_moving_to_target(drive, target_direction, current_direction, 0.7, 0.3)
    elif current_radius < radius - error:
        drive.set_speeds(0.7, 0.3)
    else:
        drive.set_speeds(0.3, 0.7)

def adjust_to_face_target_direction(drive, target_direction, current_direction):
    speed1 = 0.75
    if (current_direction - target_direction) % 360.0 <= 180.0:
        drive.set_speeds(-speed1, speed1)
    else:
        drive.set_speeds(speed1, -speed1)

def adjust_while_moving_to_target(drive, target_direction, current_direction, speed1, speed2):
    relative_angle = (current_direction - target_direction) % 360.0
    angle_threshold = 3.0
    if relative_angle <= angle_threshold or relative_angle >= 360.0 - angle_threshold:
        drive.set_speeds(speed1, speed1)
    elif relative_angle <= 180.0:
        drive.set_speeds(speed2, speed1)
    else:
        drive.set_speeds(speed1, speed2)

def reached_point(start_point, target_point, current_point):
    # handle the case where the slope would be undefined
    if start_point[1] == target_point[1]:
        if start_point[0] >= target_point[0]:
            return (current_point[0] <= target_point[0])
        else:
            return (current_point[0] >= target_point[0])

    # calculate the slope of the boundary line
    slope = -(target_point[0] - start_point[0]) / (target_point[1] - start_point[1])
    y = (slope * (current_point[0] - target_point[0])) + target_point[1]
    if start_point[1] > target_point[1]:
        return (y >= current_point[1])
    else:
        return (y <= current_point[1])

if __name__ == "__main__":
    print("Setting up drive")
    #socket = ProtoSocket(port = 8003, device = Device.AUTONOMY, destination = ("127.0.0.1", 8001))
    drive = Drive() #drive = Drive(socket) # AutonomyRover()

    print("Setting up gps...")
    gps = GPSReader()

    print("Setting up imu...")
    imu = Imu()

    print("Setting up camera...")
    camera = ObstacleDetectionCamera(1.8, 240, -0.3) #camera = DepthCamera()

    print("Setting up ultrasonic...")
    ultrasonic = Ultrasonic()

    print("Starting main")
    try:
        main2(drive, gps, imu, camera, ultrasonic)
    finally:
        print("shit")
        drive.set_speeds(0.0, 0.0)
        gps.stop_reading()
        imu.stop_reading()
        ultrasonic.stop_reading()
        ultrasonic.clean_up()
        time.sleep(2)

"""
class AutonomyProcess(Process):
    def run(self): 
        drive = Tank() # AutonomyRover()
        gps = GPSReader()
        imu = Imu()
        camera = None #camera = DepthCamera()
        try:
            main(drive, gps, imu, camera)
        finally:
            print("shit")
            drive.send_drive_data(0.0, 1.0, 1.0)
    
    def close(self): 
        print("Closing...")
        self.terminate()
        super().close()
"""
