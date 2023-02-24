import time
import sys
from lib.marker import Marker
import socket
from lib.tank import Tank
from lib.autonomy_drive import AutonomyRover

def main(drive, camera):
    #values to play around with
    search_speed = 0.6
    adjust_speed = 0.5
    middle_screen_value = 500.0
    screen_width = 1000.0
    target_range = 10.0
    move_forward_time = 2.0

    # yeah, that's right, I turn counter-clockwise
    drive.send_drive_data(search_speed, -1.0, 1.0)

    # info used in loop
    left_marker_id = 4
    right_marker_id = 0
    marker_found = False
    while True:
        marker_info = camera.read_markers()
        if len(marker_info) == 0 and not marker_found:
            continue
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
            diff = middle_screen_value - float((x1 + x2) / 2.0)
            if abs(diff) < target_range:
                break
            if diff < 0.0:
                drive.send_drive_data(adjust_speed, -1.0, 1.0)
            else:
                drive.send_drive_data(adjust_speed, 1.0, -1.0)
    
    # some stupid code but whatever
    drive.send_drive_data(0.0, 0.0, 0.0)
    time.sleep(1.0)
    drive.send_drive_data(search_speed, 1.0, 1.0)
    time.sleep(move_forward_time)
    drive.send_drive_data(0.0, 0.0, 0.0)
    camera.clean_up()

if __name__ == "__main__":
    drive = Tank()  # or Rover()
    camera = Marker()
    try:
        main(drive, camera)
    finally:
        drive.send_drive_data(0.0, 0.0, 0.0)
