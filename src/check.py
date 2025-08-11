import cv2
import cv2.aruco as aruco

class Marker:
    def __init__(self, dict_type=aruco.DICT_6X6_250):
        try:
            # Use getPredefinedDictionary instead of Dictionary_get
            self.aruco_dict = aruco.getPredefinedDictionary(dict_type)
            self.parameters = aruco.DetectorParameters()
            print("ArUco Dictionary and Detector Parameters initialized successfully.")
        except AttributeError as e:
            print("Error initializing ArUco Dictionary or Detector Parameters:", e)

# Example usage
marker = Marker()
