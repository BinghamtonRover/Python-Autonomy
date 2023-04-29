from lib.pathfinding import Pathfinding
from lib.imu.imu import Imu
from lib.gps_reader import GPSReader
from lib.drive import Drive
from network import ProtoSocket, Device
import time

def main(drive, gps, imu, camera):
    drive.set_speeds(0.0, 0.0)
    speed1 = 0.8
    print("starting")
    time.sleep(5.0)
    pathfinding = Pathfinding(gps, imu, camera, (42.08747, -75.96749))
    while (not pathfinding.is_at_goal()):
        print("running pathfinding")
        target_cords = pathfinding.pathfinding()
        current_direction = imu.get_orientation()[2] % 360.0
        start_point = gps.read_gps()
        target_direction = pathfinding.get_direction(start_point, target_cords)
        while not pathfinding.rotational_equality(target_direction, current_direction):
            adjust_to_face_target_direction(drive, target_direction, current_direction)
            current_direction = imu.get_orientation()[2] % 360.0
        drive.set_speeds(speed1, speed1)
        gps_pos = gps.read_gps()
        while not reached_point(start_point, target_cords, gps_pos): # and not is_blocked
            gps_pos = gps.read_gps()
            target_direction = pathfinding.get_direction(gps_pos, target_cords)
            current_direction = imu.get_orientation()[2] % 360.0
            adjust_while_moving_to_target(drive, target_direction, current_direction)
        drive.set_speeds(0.0, 0.0)
    print("at goal")
    drive.set_speed(0.0, 0.0)

def adjust_to_face_target_direction(drive, target_direction, current_direction):
    speed1 = 0.65
    if (current_direction - target_direction) % 360.0 <= 180.0:
        drive.set_speeds(-speed1, speed1)
    else:
        drive.set_speeds(speed1, -speed1)

def adjust_while_moving_to_target(drive, target_direction, current_direction):
    speed1 = 0.8
    speed2 = 0.65
    relative_angle = (current_direction - target_direction) % 360.0
    angle_threshold = 8.0
    if relative_angle <= angle_threshold or relative_angle >= 360.0 - angle_threshold:
        drive.set_speeds(speed1, speed1)
    elif relative_angle <= 180.0:
        drive.set_speeds(speed2, speed1)
    else:
        drive.set_speeds(speed1, speed2)

if __name__ == "__main__":
    print("Setting up drive")
    socket = ProtoSocket(port = 8003, device = Device.AUTONOMY, destination = ("127.0.0.1", 8001))
    drive = Drive(socket) # AutonomyRover()

    print("Setting up gps...")
    gps = GPSReader()

    print("Setting up imu...")
    imu = Imu()

    print("Setting up camera...")
    camera = None #camera = DepthCamera()

    print("Starting main")
    try:
        main(drive, gps, imu, camera)
    finally:
        print("shit")
        drive.set_speeds(0.0, 0.0)

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
    return (y <= current_point[1])

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
