import sys
sys.path.append("/home/pi/.local/lib/python3.9/site-packages")
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

    #dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)  # 250
    #parameters =  cv2.aruco.DetectorParameters()
    #detector = cv2.aruco.ArucoDetector(dictionary, parameters)
    
    dictionary = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)
    parameters = cv2.aruco.DetectorParameters_create()

    # usb camera
    vid_stream = VideoStream(src=0).start()
    # realsense camera
    #vid_stream = VideoStream(src=4).start()

    marker_dict = {
        0: "Start",
        1: "Post 1",
        2: "Post 2",
        3: "Post 3",
        4: "Gate Left",
        5: "Gate Right"
    }
    
    initialized = True

def detect_marker(frame):
    if (not initialized):
        return -1

    corners, ids, rejected = cv2.aruco.detectMarkers(frame, dictionary, parameters = parameters)
    #print("looking for marker")

    if len(corners):
        ids = ids.flatten()
        #print("id =", ids[0])
        center = get_marker_position(ids, corners)
        return (ids[0], center[0], center[1])
    return (-1, 0, 0)

# Analyze frames from video stream
def read_camera_for_marker():
    # Get frame from camera
    frame = vid_stream.read()
    frame = imutils.resize(frame, width=1000)

    # Look for marker, return id
    #cv2.imshow("Camera Feed", frame)
    #cv2.waitKey()
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

def get_marker_position(ids, corners):
    # If we found an ARUCO code
    for (markerCorner, markerID) in zip(corners, ids):
        corners = markerCorner.reshape((4,2))
        (topLeft, topRight, bottomLeft, bottomRight) = corners

        # Get corners of the code
        topLeft = (int(topLeft[0]), int(topLeft[1]))
        topRight = (int(topRight[0]), int(topRight[1]))
        bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
        bottomRight = (int(bottomRight[0]), int(bottomRight[1]))

        # Calculates center
        center = (int((topLeft[0] + bottomLeft[0]) / 2), int((topLeft[1] + bottomLeft[1]) / 2))
        return center
            

def clean_up():
    # Clean-up
    cv2.destroyAllWindows()
    vid_stream.stop()

"""
initialize_marker_detection()
while True:
    x = read_camera_for_marker()
    print(x)    
    #time.sleep(1)
"""
