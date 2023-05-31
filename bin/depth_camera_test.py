from lib.cameras.obstacle_avoidance import ObstacleDetectionCamera
import time
import math
import os

# update areas that are blocked based on camera data by computing the coordinates where obstacles are located
camera_horizontal_fov = 90.0
compass_direction = 0.0
current_position = (0, 0)

def _update_blocked_areas(depth_lists):
    grid_ticker = {}
    max_ticks = 40
    for l in depth_lists:
        current_angle = ((-camera_horizontal_fov / 2.0) + compass_direction) % 360.0
        for d in l:
            if d != -1.0 and d != 0.0:
                pos = (math.floor(current_position[0] + d * math.cos(current_angle * (math.pi / 180.0))), math.floor(current_position[1] + d * math.sin(current_angle * (math.pi / 180.0))))
                if pos[0] < 0.0:
                    print(pos)
                if pos in grid_ticker:
                    grid_ticker[pos] += 1
                else:
                    grid_ticker[pos] = 1
            current_angle += (camera_horizontal_fov / (len(l) - 1.0))
            if current_angle >= 360.0:
                current_angle -= 360.0
    out_list = []
    for k in grid_ticker:
        if grid_ticker[k] >= max_ticks:
            os.system("clear")
            if k == current_position:
                print("blocked")
                out_list.append((math.floor(k[0] + math.cos(compass_direction)), math.floor(k[1] + math.sin(compass_direction))))
            out_list.append(k)
    print(out_list)

def main():
    print("Started")
    camera = ObstacleDetectionCamera(2.4, 50, -0.3)
    print("Initialized")
    fun = lambda a : int(a)
    time.sleep(5)
    #while True:
    #    print(camera.read_markers())

    while True:
        #print(camera.is_blocked())
        print(camera.get_distances(20))

    while True:
        y = camera.get_distances([40])
        _update_blocked_areas(y)
        time.sleep(1.0)

if __name__ == "__main__":
    main()
