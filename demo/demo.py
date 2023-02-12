import time
import sys
import driver as camera
import socket
from tank import Tank

drive = None

def read_marker():
    # plan to return marker horizontal location on screen
    return camera.read_camera_for_marker()

def send_right_speed(speed):
    drive.set_right_velocity(speed)

def send_left_speed(speed):
    drive.set_left_velocity(speed)
    
def move_forward(speed):
    send_left_speed(speed)
    send_right_speed(speed)

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

def main():
    global drive

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
    drive = Tank()
    camera.initialize_marker_detection()
    
    time.sleep(4)

    # yeah, that's right, I turn counter-clockwise
    send_left_speed(-search_speed)
    send_right_speed(search_speed)

    x_pos = None
    while True:
        x_pos = read_marker()
        #print(read_marker())
        if x_pos[0] != -1:
            diff = middle_screen_value - float(x_pos[1])
            if abs(diff) < target_range:
                break
            elif diff < 0.0:
                send_left_speed(-adjust_speed)
                send_right_speed(adjust_speed)
            else:
                send_left_speed(adjust_speed)
                send_right_speed(-adjust_speed)
            #adjust_speed = get_adjust_speed(search_speed, min_adjust_speed, middle_screen_value, screen_width)
            #send_left_speed(-adjust_speed)
            #send_right_speed(adjust_speed)
        if wait_in_loops:
            time.sleep(wait_time)
            
    move_forward(0.0)
    
    time.sleep(0.5)

    move_forward(search_speed)

    time.sleep(move_forward_time)

    move_forward(0.0)
    
    camera.clean_up()

if __name__ == "__main__":
    try:
        main()
    finally:
        move_forward(0.0)
