import time
import sys
from marker import driver
from driver import *

def read_marker():
    # plan to return marker horizontal location on screen
    return -1.0

def send_right_speed():
    return

def send_left_speed():
    return

def get_adjust_speed(search_speed, min_speed, target, width):
    dist_to_target = abs(width - target)
    adjust_speed = ((2.0 * (search_speed - min_speed)) / width) + min_speed
    
    # in case slightly off values are provided somehow
    if adjust_speed > search_speed:
        adjust_speed = search_speed
    if adjust_speed < min_speed:
        adjust_speed = min_speed
    return adjust_speed

def main():
    #values to play around with
    search_speed = 8.0
    min_adjust_speed = 2.0
    middle_screen_value = 320.0
    screen_width = 640.0
    target_range = 1.0
    move_forward_time = 5.0

    # just in case we need a delay, this will do for a demo
    wait_in_loops = True
    wait_time = 0.1

    # initialization
    initialize_marker_detection()

    # yeah, that's right, I turn counter-clockwise
    send_left_speed(-search_speed)
    send_right_speed(search_speed)

    x_pos = None
    while True:
        x_pos = read_marker()
        print(read_marker())
        if x_pos != -1:
            break
        if wait_in_loops:
            time.sleep(wait_time)
    
    while True:
        x_pos = read_marker()
        if abs(middle_screen_value - x_pos) < target_range:
            break
        adjust_speed = get_adjust_speed(search_speed, min_adjust_speed, middle_screen_value, screen_width)
        send_left_speed(-adjust_speed)
        send_right_speed(adjust_speed)
        if wait_in_loops:
            time.sleep(wait_time)

    send_left_speed(search_speed)
    send_right_speed(search_speed)

    time.sleep(move_forward_time)

    send_left_speed(0.0)
    send_right_speed(0.0)

if __name__ == "__main__":
    sys.exit(main())