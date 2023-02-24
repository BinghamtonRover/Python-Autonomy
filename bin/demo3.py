import time
import sys
from lib.marker import Marker
import socket
from lib.tank import Tank
#from lib.autonomy_drive import AutonomyRover

def main(drive, camera):
    #values to play around with
    search_speed = 0.7
    adjust_speed = 0.5
    middle_screen_value = 500.0
    screen_width = 1000.0
    target_range = 15.0
    move_forward_time = 2.0
    marker_offset = 100.0
    
    time.sleep(5)

    # yeah, that's right, I turn counter-clockwise (left)
    drive.send_drive_data(search_speed, -1.0, 1.0)

    while True:
        marker_info = camera.read_markers()
        if len(marker_info) != 2:
            continue
        else:
            x1 = marker_info[0][1]
            x2 = marker_info[1][1]
            diff = middle_screen_value - float((x1 + x2) / 2.0) + marker_offset
            if abs(diff) < target_range:
                break
            if diff < 0.0:
                drive.send_drive_data(adjust_speed, 1.0, -1.0)
            else:
                drive.send_drive_data(adjust_speed, -1.0, 1.0)
    
    # some stupid code but whatever
    drive.send_drive_data(0.0, 0.0, 0.0)
    time.sleep(1.0)
    
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
                drive.send_drive_data(search_speed, 1.0, 1.0)
            if diff < 0.0:
                drive.send_drive_data(search_speed, 1.0, 0.8)
            else:
                drive.send_drive_data(search_speed, 0.8, 1.0)

    drive.send_drive_data(0.0, 0.0, 0.0)
    camera.clean_up()

if __name__ == "__main__":
    drive = Tank()  # or Rover()
    camera = Marker()
    try:
        main(drive, camera)
    finally:
        drive.send_drive_data(0.0, 0.0, 0.0)
