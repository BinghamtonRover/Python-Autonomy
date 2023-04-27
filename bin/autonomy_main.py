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
        target_direction = pathfinding.pathfinding()
        current_direction = imu.get_orientation()[2] % 360.0
        print(str(target_direction))
        while not pathfinding.rotational_equality(target_direction, current_direction):
            #print(str(target_direction))
            #print(str(current_direction))
            adjust_to_face_target_direction(drive, target_direction, current_direction)
            current_direction = imu.get_orientation()[2] % 360.0
        drive.set_speeds(speed1, speed1)
        print("this is right")
        time.sleep(2)
        drive.set_speeds(0.0, 0.0)
    print("at goal")
    drive.set_speed(0.0, 0.0)

def adjust_to_face_target_direction(drive, target_direction, current_direction):
    speed1 = 0.65
    if target_direction > 0.0:
        if current_direction < target_direction and current_direction > target_direction - 180.0:
            drive.set_speeds(speed1, -speed1)
            pass
        else:
            drive.set_speeds(-speed1, speed1)
            pass
    else:
        if current_direction > target_direction and current_direction < target_direction + 180.0:
            drive.set_speeds(-speed1, speed1)
            pass
        else:
            drive.set_speeds(speed1, -speed1)
            pass

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
