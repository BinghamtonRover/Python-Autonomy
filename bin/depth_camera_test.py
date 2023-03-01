from lib.depth_camera import DepthCamera

def main():
    print("Started")
    camera = DepthCamera()
    print("Initialized")
    while True:
        print(camera.get_distances(1))

if __name__ == "__main__":
    main()