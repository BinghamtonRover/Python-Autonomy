from lib.depth_camera import DepthCamera
from lib.obstacle_avoidance import ObstacleDetectionCamera

def main():
    print("Started")
    camera = ObstacleDetectionCamera(2.4, 240, -0.3)
    print("Initialized")
    x = lambda a : float(int(a * 100.0)) / 100.0
    while True:
        print(list(map(x, camera.get_distances(20))))

if __name__ == "__main__":
    main()