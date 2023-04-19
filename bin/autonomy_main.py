from lib.pathfinding import Pathfinding
from lib.depth_camera import DepthCamera
from lib.imu.imu import Imu
from lib.gps_reader import GPSReader
import time

def main(drive, gps, imu, camera):
    speed1 = 0.7
    pathfinding = Pathfinding(gps, imu, camera, (42.08741, 75.96748))
    while (not pathfinding.is_at_goal()):
        target_direction = pathfinding.pathfinding()
        current_direction = imu.get_orientation()[2]
        print(str(target_direction))
        while not pathfinding.rotational_equality(target_direction, current_direction)
            print(str(target_direction))
            adjust_to_face_target_direction(drive, target_direction, current_direction)
        drive.send_drive_data(self.speed1, 0.0, 0.0)
        time.sleep(2)
        drive.send_drive_data(0.0, 0.0, 0.0)

def adjust_to_face_target_direction(drive, target_direction, current_direction):
    speed1 = 0.7
    if target_direction > 0.0:
        if current_direction < target_direction and current_direction > target_direction - 180.0
            drive.send_drive_data(speed1, 1.0, -1.0)
        else:
            drive.send_drive_data(speed1, -1.0, 1.0)
    else:
        if current_direction > target_direction and current_direction < target_direction + 180.0:
            drive.send_drive_data(speed1, -1.0, 1.0)
        else:
            drive.send_drive_data(speed1, 1.0, -1.0)

if __name__ == "__main__":
    drive = Tank() # AutonomyRover()
    gps = GPSReader()
    imu = Imu()
    camera = None #camera = DepthCamera()
    try:
        main(drive, gps, imu, camera)
    finally:
        print("shit")
        drive.send_drive_data(0.0, 1.0, 1.0)

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
