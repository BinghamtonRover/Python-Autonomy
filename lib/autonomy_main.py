from lib.pathfinding import Pathfinding
from lib.hardware.imu import Imu
from lib.hardware.gps_reader import GPSReader
from lib.network.drive import Drive
from lib.cameras.obstacle_avoidance import ObstacleDetectionCamera
#from network import ProtoSocket, Device
import time
import math
import sys

class Autonomy:
    def __init__(self):
        self.previous_left_ultrasonic = -1.0
        self.left_ultrasonic = -1.0
        self.previous_right_distance = -1.0
        self.right_ultrasonic = -1.0

    def autonomy_to_cords(self, collection):
        self._main(collection.drive, collection.gps, collection.imu, collection.camera, collection.subsystems, collection.dashboard)

    def autonomy_to_marker(self, collection, radius):
        self._main2(collection.drive, collection.gps, collection.imu, collection.camera, collection.subsystems, collection.dashboard, 20.0)

    def _main2(self, drive, gps, imu, camera, subsystems, dashboard, marker_radius):
        pathfinding = Pathfinding(gps, imu, camera, targets[0], subsystems, dashboard)

        self._pathfind_to_find_marker(drive, gps, imu, camera, subsystems, pathfinding, dashboard, marker_radius)

        targets = self._get_targets(gps_goal, marker_radius)

        at_marker = False
        while not at_marker:
            self.dashboard.send_message(AutonomyData(state = AutonomyState.SEARCHING))
            while len(camera.read_markers()) == 0:
                pathfinding = Pathfinding(gps, imu, camera, targets[0])
                del targets[0]
                if len(targets) == 0:
                    targets = self._get_targets(gps_goal, marker_radius)
                self._pathfind_to_find_marker(drive, gps, imu, camera, subsystems, pathfinding, 2.0)

            self.dashboard.send_message(AutonomyData(state = AutonomyState.APPROACHING))
            done = False
            while True:
                info = self._get_second_marker_info(camera.read_markers(), -1)
                if len(info) != 0:
                    if info[1] > 330:
                        drive.set_speeds(-0.7, 0.7)
                    elif info[1] < 310:
                        drive.set_speeds(0.7, -0.7)
                    elif info[3] > 1.5:
                        drive.set_speeds(0.8, 0.8)
                    else:
                        at_marker = True
                        break
                else:
                    break

        self.dashboard.send_message(AutonomyData(state = AutonomyState.AT_DESTINATION))
        drive.set_speeds(0.0, 0.0)
        print("done")

    def _get_targets(center, radius):
        radius *= 1.414
        targets = []
        for i in range(math.ceil(radius), 1, -1):
            targets.append((center[0] + i * (0.00001 / 1.11), center[1]))
            targets.append((center[0], center[1] + i * (0.00001 / 1.11)))
            targets.append((center[0] - i * (0.00001 / 1.11), center[1]))
            targets.append((center[0], center[1] + i * (0.00001 / 1.11)))
        targets.append(center)

    def _pathfind_to_find_marker(drive, gps, imu, camera, subsystems, pathfinding, dashboard, marker_radius):
        speed1 = 0.9
        # go to gps location
        while (not pathfinding.is_at_goal(marker_radius) and len(camera.read_markers()) == 0):
            print("running pathfinding")
            self.dashboard.send_message(AutonomyData(state = AutonomyState.PATHING))
            target_cords = pathfinding.pathfinding()
            current_direction = imu.get_orientation()[2] % 360.0
            start_point = gps.read_gps()
            target_direction = pathfinding.get_direction(start_point, target_cords)
            self.dashboard.send_message(AutonomyData(state = AutonomyState.DRIVING))
            while not pathfinding.rotational_equality(target_direction, current_direction) and len(camera.read_markers()) == 0:
                self._adjust_to_face_target_direction(drive, target_direction, current_direction)
                current_direction = imu.get_orientation()[2] % 360.0
            drive.set_speeds(speed1, speed1)
            gps_pos = gps.read_gps()
            while not self._reached_point(start_point, target_cords, gps_pos) and subsystems.is_drivable() and (not camera.is_blocked()) and len(camera.read_markers()) == 0:
                gps_pos = gps.read_gps()
                target_direction = pathfinding.get_direction(gps_pos, target_cords)
                current_direction = imu.get_orientation()[2] % 360.0
                self._adjust_while_moving_to_target(drive, target_direction, current_direction, 0.9, 0.4)
            if not subsystems.is_drivable():
                drive.set_speeds(-0.9, -0.9)
                time.sleep(0.5)
            drive.set_speeds(0.0, 0.0)
        drive.set_speeds(0.0, 0.0)
        print("done!")

    def _main(drive, gps, imu, camera, subsystems, dashboard, gps_goal):
        # go to gps location
        self.dashboard.send_message(AutonomyData(state = AutonomyState.PATHING))
        while (not pathfinding.is_at_goal(1.0)):
            print("running pathfinding")
            target_cords = pathfinding.pathfinding()
            current_direction = imu.get_orientation()[2] % 360.0
            start_point = gps.read_gps()
            target_direction = pathfinding.get_direction(start_point, target_cords)
            while not pathfinding.rotational_equality(target_direction, current_direction):
                self._adjust_to_face_target_direction(drive, target_direction, current_direction)
                current_direction = imu.get_orientation()[2] % 360.0
            drive.set_speeds(speed1, speed1)
            gps_pos = gps.read_gps()
            while not self._reached_point(start_point, target_cords, gps_pos) and subsystems.is_drivable() and (not camera.is_blocked()):
                gps_pos = gps.read_gps()
                target_direction = pathfinding.get_direction(gps_pos, target_cords)
                current_direction = imu.get_orientation()[2] % 360.0
                self._adjust_while_moving_to_target(drive, target_direction, current_direction, 0.9, 0.4)
            drive.set_speeds(0.0, 0.0)
        self.dashboard.send_message(AutonomyData(state = AutonomyState.AT_DESTINATION))
        drive.set_speeds(0.0, 0.0)
        print("done!")

    def _get_second_marker_info(camera_info, first_id):
        for i in markers:
            if i[0] != first_id:
                return i
        return []

"""
    def _drive_spiral(drive, current_rotation, current_position, origin, radius):
        rotation_vector = (-(current_position[1] - origin[1]), current_position[0] - origin[0])
        current_radius = math.sqrt(math.pow(rotation_vector[0], 2) + math.pow(rotation_vector[1], 2))
        target_direction = (math.atan2(-rotation_vector[1], rotation_vector[0]) * (180.0 / math.pi)) % 360.0
        error = 0.1
        if current_radius >= radius - error and current_radius <= radius + error:
            _adjust_while_moving_to_target(drive, target_direction, current_direction, 0.7, 0.3)
        elif current_radius < radius - error:
            drive.set_speeds(0.7, 0.3)
        else:
            drive.set_speeds(0.3, 0.7)
"""

    def _adjust_to_face_target_direction(drive, target_direction, current_direction):
        speed1 = 0.75
        if (current_direction - target_direction) % 360.0 <= 180.0:
            drive.set_speeds(-speed1, speed1)
        else:
            drive.set_speeds(speed1, -speed1)

    def _adjust_while_moving_to_target(drive, target_direction, current_direction, speed1, speed2):
        relative_angle = (current_direction - target_direction) % 360.0
        angle_threshold = 3.0
        if relative_angle <= angle_threshold or relative_angle >= 360.0 - angle_threshold:
            drive.set_speeds(speed1, speed1)
        elif relative_angle <= 180.0:
            drive.set_speeds(speed2, speed1)
        else:
            drive.set_speeds(speed1, speed2)

    def _reached_point(start_point, target_point, current_point):
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

    """
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
        # TODO create ultrasonic objects for left and right (it shouldn't matter if they are flipped btw)
        ultrasonic_left = Ultrasonic()
        ultrasonic_right = Ultrasonic()

        print("Starting main")
        try:
            main2(drive, gps, imu, camera, ultrasonic_left, ultrasonic_right)
        finally:
            # TODO on the rover we don't want to close all of this, we want it to be passed in
            print("shit")
            drive.set_speeds(0.0, 0.0)
            gps.stop_reading()
            imu.stop_reading()
            ultrasonic_left.stop_reading()
            ultrasonic_right.stop_reading()
            time.sleep(1)
            ultrasonic_left.clean_up()
            ultrasonic_right.clean_up()
            time.sleep(2)
    """
