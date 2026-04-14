from tracker import GazeTracker
import os
import cv2

class GazeManager:
    def __init__(self):
        self.gaze_tracker = GazeTracker(model_path="itracker_baseline.tar")

        # Retrieve the webcam URL from environment variables
        self.webcam_url: str = os.getenv("WEBCAM_URL", "0")  # Default to "0" for local webcam

        self.webcam = cv2.VideoCapture(self.webcam_url if self.webcam_url != "0" else 0)
        self.openWebcam()


    def openWebcam(self):
        """If the webcan is not already opened, try to open it, and print an error if needed"""
        if not self.webcam.isOpened():
            self.webcam = cv2.VideoCapture(self.webcam_url if self.webcam_url != "0" else 0)
            if not self.webcam.isOpened():
                print("Unable to open webcam. Please check your device or URL.")
                return

    def calibrate(self):
        """Launch Model Calibration for the user"""
        self.openWebcam()

        self.gaze_tracker.calibrate(self.webcam);

    def getGazeCoords(self, face_mesh):
        return self.gaze_tracker.getGazeCoord(self.webcam, face_mesh)
