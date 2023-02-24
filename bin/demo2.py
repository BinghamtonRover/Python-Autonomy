import time
import sys
from lib.marker import Marker
import socket
from lib.tank import Tank
from lib.depth_camera import DepthCamera
#from lib.autonomy_drive import AutonomyRover

def main(drive, depth_camera, camera):
    #values to play around with
    rotation_speed = 0.7
    forward_speed = 0.5
    middle_screen_value = 500.0
    screen_width = 1000.0
    blocked_dist = 0.00085
    total_time = 120.0
    
    #while True:
    #    print(depth_camera.get_distances(3))

    time.sleep(6.0)
    
    drive.send_drive_data(forward_speed, 1.0, 1.0)
    time.sleep(0.4)
    drive.send_drive_data(0.0, 1.0, 1.0)
    time.sleep(0.4)
    drive.send_drive_data(-forward_speed, 1.0, 1.0)
    time.sleep(0.4)
    
    start_time = time.perf_counter()
    sleepy_time = False
    
    left_marker_id = 4
    right_marker_id = 0
    marker_found = False

    while not sleepy_time and (time.perf_counter() - start_time) < total_time:
        dists = depth_camera.get_distances(3)
        marker_info = [] #camera.read_markers()
        if dists[0] == 0.0 and dists[1] == 0.0 and dists[2] == 0.0:
            sleepy_time = True
        if len(marker_info) == 0 and not marker_found:
            left = dists[0] < blocked_dist
            middle = dists[1] < blocked_dist
            right = dists[2] < blocked_dist
            if middle:
                if left:
                    drive.send_drive_data(rotation_speed, 1.0, -1.0)
                elif right:
                    drive.send_drive_data(rotation_speed, -1.0, 1.0)
                else:
                    drive.send_drive_data(rotation_speed, -1.0, 1.0)
            elif left:
                drive.send_drive_data(rotation_speed, 1.0, -1.0)
            elif right:
                drive.send_drive_data(rotation_speed, -1.0, 1.0)
            else:
                drive.send_drive_data(forward_speed, 1.0, 1.0)
        elif len(marker_info) == 0 and marker_found:
            break
        elif len(marker_info) == 1:
            marker_id = marker_info[0][0]
            x_pos = marker_info[0][1]
            if marker_id == left_marker_id:
                diff = x_pos
                if diff < target_range:
                    break
                else:
                    drive.send_drive_data(adjust_speed, 1.0, -1.0)
            elif marker_id == right_marker_id:
                diff = screen_width - x_pos
                if diff < target_range:
                    drive.send_drive_data(adjust_speed, -1.0, 1.0)
                else:
                    break
        # this case may not be possible (because of distance), but I'm leaving it in just in case it is
        elif len(marker_info) == 2:
            x1 = marker_info[0][1]
            x2 = marker_info[1][1]
            diff = middle_screen_value - float(x_pos[1])
            if abs(diff) < target_range:
                break
            if diff < 0.0:
                drive.send_drive_data(adjust_speed, -1.0, 1.0)
            else:
                drive.send_drive_data(adjust_speed, 1.0, -1.0)
        
    #drive.send_drive_data(0.0, 0.0, 0.0)
    #time.sleep(1.0)
    #drive.send_drive_data(search_speed, 1.0, 1.0)
    #time.sleep(move_forward_time)
    #drive.send_drive_data(0.0, 0.0, 0.0)
    #camera.clean_up()


if __name__ == "__main__":
    drive = Tank()  # or Rover()
    camera = None # Marker()
    depth_camera = DepthCamera()
    try:
        main(drive, depth_camera, camera)
    finally:
        print("shit")
        drive.send_drive_data(0.0, 0.0, 0.0)
        depth_camera.clean_up()

