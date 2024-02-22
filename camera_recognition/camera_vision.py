import cv2
import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from camera_recognition.utils import visualize

import time

# Global variables to calculate FPS
COUNTER, FPS = 0, 0
START_TIME = time.time()

USE_MODEL = False

class VisionCamera():
    def __init__(self):
        self.initParameters()
        self.initCamera()
        if USE_MODEL:
            self.initModel()
            self.detection_frame = None
            self.detection_result_list = []
        print("Camera vision initialized")
        # self.start()

    def initParameters(self):
        # self.model = "camera_recognition/efficientdet.tflite"
        self.model = "camera_recognition/efficientdet.tflite"
        self.maxResults = 5
        self.scoreThreshold = 0.7
        self.cameraID = 0
        self.cameraHeight = 720
        self.cameraWidth = 1280

    def initCamera(self):
        self.camera = cv2.VideoCapture(self.cameraID, cv2.CAP_V4L2)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.cameraWidth)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.cameraHeight)

    def initModel(self):
        self.fps_avg_frame_count = 10

        base_options = python.BaseOptions(model_asset_path=self.model)
        options = vision.ObjectDetectorOptions(base_options=base_options,
                                         running_mode=vision.RunningMode.LIVE_STREAM,
                                         max_results=self.maxResults, score_threshold=self.scoreThreshold,
                                         result_callback=self.save_result)

        self.detector = vision.ObjectDetector.create_from_options(options)

    def runModel(self, image):
        if not USE_MODEL:
            return image
        # Convert the image from BGR to RGB as required by the TFLite model.
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)

        # Run object detection using the model.
        self.detector.detect_async(mp_image, time.time_ns() // 1_000_000)
        for detect in self.detection_result_list:
                    image = visualize(image, detect)
                    # detection_frame = current_frame
                    self.detection_result_list.clear()
        return image

    def save_result(self, result: vision.ObjectDetectorResult, unused_output_image: mp.Image, timestamp_ms: int):
      global FPS, COUNTER, START_TIME

      # Calculate the FPS
      if COUNTER % self.fps_avg_frame_count == 0:
          FPS = self.fps_avg_frame_count / (time.time() - START_TIME)
          START_TIME = time.time()

      self.detection_result_list.append(result)
      COUNTER += 1

    def videoPhoto(self):
        success, image = self.camera.read()
        if not success:
            print("Failed to capture image.")
            return

        image = cv2.flip(image, 1)

        if USE_MODEL:                
            image = self.runModel(image)

        cv2.imshow('Camera Feed', image)
        cv2.imwrite("image.jpg", image)


    def getPhoto(self):
        success, image = self.camera.read()
        if success:
            ret, buffer = cv2.imencode('.jpg', image)
            print("CHUJ")
            if ret:  # Ensure encoding was successful
                frame = buffer.tobytes()
                print("Udalo sie!")
                self.camera.release()
                return frame 
        # If capture or encoding fails, return a default image or error frame
        self.camera.release()
        return b'Error frame or some default image bytes'


    def start(self):
        if not self.camera.isOpened():
            print("Failed to open camera.")
            return

        while True:
            self.videoPhoto()
            # Break the loop with the ESC key
            if cv2.waitKey(1) & 0xFF == 27:
                break

        self.camera.release()
        cv2.destroyAllWindows()


# def main():
#     try:
#         v = VisionCamera()
#         v.start()
#     except Exception as e:
#         print("Exeption was caught: "+ str(e))

# if __name__ == '__main__':
#     main()