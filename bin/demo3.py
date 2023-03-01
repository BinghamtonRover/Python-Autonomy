import time
import sys
from lib.marker import Marker
import socket
from lib.tank import Tank
from lib.depth_camera import DepthCamera
from lib.text_drive import TextDrive
#from lib.autonomy_drive import AutonomyRover

def main(drive, camera):
    #values to play around with
    search_speed = 0.75
    adjust_speed = 0.5
    forward_speed = 0.8
    middle_screen_value = 500.0
    screen_width = 1000.0
    target_range = 50.0
    move_forward_time = 3.0
    marker_offset = 100.0
    
    time.sleep(5)

    # yeah, that's right, I turn counter-clockwise (left)
    drive.send_drive_data(search_speed, -1.0, 1.0)
    first_time_found = True
    
    print("first search")
    # Part 1, look for markers
    while True:
        marker_info = camera.read_markers()
        if len(marker_info) != 2:
            continue
        else:
            if first_time_found:
                first_time_found = False
                print("found markers")
            x1 = marker_info[0][1]
            x2 = marker_info[1][1]
            diff = middle_screen_value - float((x1 + x2) / 2.0) + marker_offset
            if abs(diff) < target_range:
                break
            if diff < 0.0:
                drive.send_drive_data(adjust_speed, 1.0, -1.0)
            else:
                drive.send_drive_data(adjust_speed, -1.0, 1.0)
    print("adjusted")
    drive.send_drive_data(0.0, 1.0, 1.0)
    time.sleep(1.0)
    drive.send_drive_data(1.0, 1.0, 1.0)
    
    print("avoid obstacle")
    # Part 2, avoid obstacle that will be encountered
    blocked_dist = 0.0005
    while True:
        dists = camera.get_distances(1)
        if dists[0] < blocked_dist:
            drive.send_drive_data(0.0, 1.0, 1.0)
            break
    time.sleep(0.5)
    unblocked_dist = 0.001
    drive.send_drive_data(search_speed, -1.0, 1.0)
    while True:
        dists = camera.get_distances(1)
        if dists[0] > unblocked_dist:
            drive.send_drive_data(search_speed, 1.0, 1.0)
            break
    time.sleep(3.0)
    drive.send_drive_data(0.0, 1.0, 1.0)
    time.sleep(0.5)
    drive.send_drive_data(search_speed, 1.0, -1.0)

    print ("second search")
    # Part 3, look for markers
    while True:
        marker_info = camera.read_markers()
        if len(marker_info) != 2:
            continue
        else:
            if first_time_found:
                first_time_found = False
                print("found markers")
            x1 = marker_info[0][1]
            x2 = marker_info[1][1]
            diff = middle_screen_value - float((x1 + x2) / 2.0) + marker_offset
            if abs(diff) < target_range:
                break
            if diff < 0.0:
                drive.send_drive_data(adjust_speed, 1.0, -1.0)
            else:
                drive.send_drive_data(adjust_speed, -1.0, 1.0)
    print("adjusted")
    drive.send_drive_data(0.0, 1.0, 1.0)
    time.sleep(1.0)
    
    # Part 4, drive through gates
    print("now go all the way")
    lost_markers_time = time.perf_counter()
    while (time.perf_counter() - lost_markers_time) < move_forward_time:
        marker_info = camera.read_markers()
        if len(marker_info) != 2:
            continue
        else:
            lost_markers_time = time.perf_counter()
            x1 = marker_info[0][1]
            x2 = marker_info[1][1]
            diff = middle_screen_value - float((x1 + x2) / 2.0) + marker_offset
            if abs(diff) < target_range:
                drive.send_drive_data(forward_speed, 1.0, 1.0)
            if diff < 0.0:
                drive.send_drive_data(forward_speed, 1.0, 0.8)
            else:
                drive.send_drive_data(forward_speed, 0.8, 1.0)

    print("done")
    drive.send_drive_data(0.0, 1.0, 1.0)
    camera.clean_up()

if __name__ == "__main__":
    drive = Tank()  # or Rover()
    #camera = Marker()
    camera = DepthCamera()
    try:
        main(drive, camera)
    finally:
        print("shit")
        drive.send_drive_data(0.0, 1.0, 1.0)
