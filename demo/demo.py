import time
import sys
import demo.driver as camera
import socket
from demo.tank import Tank
from demo.autonomy_drive import AutonomyRover

def read_marker():
    # plan to return marker horizontal location on screen
    return camera.read_camera_for_marker()

"""
def get_adjust_speed(search_speed, min_speed, target, width):
    dist_to_target = abs(width - target)
    adjust_speed = ((2.0 * (search_speed - min_speed)) / width) + min_speed
    
    # in case slightly off values are provided somehow
    if adjust_speed > search_speed:
        adjust_speed = search_speed
    if adjust_speed < min_speed:
        adjust_speed = min_speed
    return adjust_speed
"""

def main(drive):
    #values to play around with
    search_speed = 6.1
    adjust_speed = 5.1
    min_adjust_speed = 2.0
    middle_screen_value = 500.0
    screen_width = 1000.0
    target_range = 10.0
    move_forward_time = 2.0

    # just in case we need a delay, this will do for a demo
    wait_in_loops = False
    wait_time = 0.01

    # initialization
    camera.initialize_marker_detection()
    
    time.sleep(4)

    # yeah, that's right, I turn counter-clockwise
    drive.send_drive_data(search_speed, -1.0, 1.0)

    x_pos = None
    while True:
        x_pos = read_marker()
        #print(read_marker())
        if x_pos[0] != -1:
            diff = middle_screen_value - float(x_pos[1])
            if abs(diff) < target_range:
                break
            elif diff < 0.0:
                drive.send_drive_data(adjust_speed, -1.0, 1.0)
            else:
                drive.send_drive_data(adjust_speed, 1.0, -1.0)
        if wait_in_loops:
            time.sleep(wait_time)
            
    drive.send_drive_data(0.0, 0.0, 0.0)
    
    time.sleep(1.0)

    drive.send_drive_data(search_speed, 1.0, 1.0)

    time.sleep(move_forward_time)

    drive.send_drive_data(0.0, 0.0, 0.0)
    
    camera.clean_up()

if __name__ == "__main__":
    drive = Tank()  # or Rover()
    try:
        main(drive)
    finally:
        drive.send_drive_data(0.0, 0.0, 0.0)
