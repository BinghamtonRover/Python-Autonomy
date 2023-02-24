import pyrealsense2 as rs
import bisect
from statistics import mean

class DepthCamera:
    def __init__(self):
        # Create a context object. This object owns the handles to all connected realsense devices
        self.pipeline = rs.pipeline()

        # Configure streams
        self.config = rs.config()
        self.config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

        # Start streaming
        self.pipeline.start(self.config)
        
        self.minY = 30
        self.maxY = 450
        self.target_mins_total = 3000.0
        self.zero_limit = 200000

    def get_distances(self, sections):
        frames = self.pipeline.wait_for_frames()
        depth = frames.get_depth_frame()
        if not depth:
            return []
        dists = []

        current_mins = []
        current_section = 0
        target_mins_per_section = int(self.target_mins_total / float(sections))
        zero_limit_per_section = int(self.zero_limit / float(sections))
        lower_data_trim = int(target_mins_per_section/2.0)
        num_zeroes = 0
        for x in range(640):
            for y in range(self.minY, self.maxY + 1):
                sect = int(float(x) / (640.0 / float(sections)))
                if sect != current_section:
                    if num_zeroes < zero_limit_per_section:
                        dists.append(mean(current_mins[int(len(current_mins)/2.0):int(len(current_mins)/1.2)]))
                    else:
                        dists.append(0.0)
                    current_mins = []
                    current_section = sect
                    num_zeroes = 0
                dist = 0.001 * depth.get_distance(x, y) #0.001 converts to meters
                if dist == 0.0:
                    num_zeroes += 1
                else:
                    if len(current_mins) < target_mins_per_section:
                        bisect.insort(current_mins, dist)
                    elif dist < current_mins[target_mins_per_section - 1]:
                        bisect.insort(current_mins, dist)
        if num_zeroes < zero_limit_per_section:
            dists.append(mean(current_mins[int(len(current_mins)/2.0):int(len(current_mins)/1.2)]))
        else:
            dists.append(0.0)
        return dists
    
    def clean_up(self):
        self.pipeline.stop()
