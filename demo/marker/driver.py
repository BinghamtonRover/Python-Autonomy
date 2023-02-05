from cgitb import html
from time import time
import cv2
import imutils
from imutils.video import VideoStream
import time
import math

dictionary = None
parameters = None
detector = None
vid_stream = None
marker_dict = None
initialized = False

# Import correct ARUCO dictionary and set up params
def initialize_marker_detection():
    global dictionary
    global parameters
    global detector
    global vid_stream
    global marker_dict
    global initialized

    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)  # 250
    parameters =  cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(dictionary, parameters)

    vid_stream = VideoStream(src=0).start()
    time.sleep(2.0)

    marker_dict = {
        0: "Start",
        1: "Post 1",
        2: "Post 2",
        3: "Post 3",
        4: "Gate Left",
        5: "Gate Right"
    }

def detect_marker(frame):
    if (not initialized):
        print("not initialized")
        return -1

    corners, ids, rejected = detector.detectMarkers(frame)
    #print("looking for marker")

    if len(corners):
        ids = ids.flatten()
        #print("id =", ids[0])
        return id

    return -1

# Analyze frames from video stream
def read_camera_for_marker():
    # Get frame from camera
    frame = vid_stream.read()
    frame = imutils.resize(frame, width=1000)

    # Look for marker, return id
    return detect_marker(frame)

    #if (detect_marker(frame) != -1):
        #print("Marker found")
            
    # Shows the camera feed
    #cv2.imshow("Camera Feed", frame)
    #key = cv2.waitKey(1) & 0xFF

"""
# Continuously analyze frames from video stream
while (True):

    # Get frame from camera
    frame = vid_stream.read()
    frame = imutils.resize(frame, width=1000)

    #corners, ids, rejected = detector.detectMarkers(frame)

    if has_marker(frame):
        print("Marker found")
            
    # Shows the camera feed
    cv2.imshow("Camera Feed", frame)
    key = cv2.waitKey(1) & 0xFF

# Breaks out of loop when we press q
    if key == ord("q"):
        break
"""

def clean_up():
    # Clean-up
    cv2.destroyAllWindows()
    vid_stream.stop()