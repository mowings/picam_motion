import io
import time, datetime
import picamera
import cv2
import numpy as np


# A simple Motion Detection algorithm.
class MotionDetection:
    def __init__(self):
        self.__image0 = None
        self.__image1 = None
        self.__image2 = None
        self._count = 0

        # Configurations
        # Change these to adjust sensitive of motion
        self._MOTION_LEVEL = 100
        self._THRESHOLD = 35

    def _updateImage(self, image):
        self.__image2 = self.__image1
        self.__image1 = self.__image0
        self.__image0 = image

    def _ready(self):
        return self.__image0 != None and self.__image1 != None and self.__image2 != None

    def _getMotion(self):
        if not self._ready():
            return None

        d1 = cv2.absdiff(self.__image1, self.__image0)
        d2 = cv2.absdiff(self.__image2, self.__image0)
        result = cv2.bitwise_and(d1, d2)

        (value, result) = cv2.threshold(result, self._THRESHOLD, 255, cv2.THRESH_BINARY)

        scalar = cv2.sumElems(result)

        # print " - scalar:", scalar[0], scalar
        return scalar

    def detectMotion(self, image):
        self._updateImage(image)

        motion = self._getMotion()
        if motion and motion[0] > self._MOTION_LEVEL:
            print "motion scalar:", motion[0], motion
            return True
        return False

    def saveImage(self, camera):
        tstmp = datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")
        image_file  = "/opt/camera/capture_%s_%05d.jpg" % (tstmp, self._count)
        camera.resolution = (1920,1080)
        camera.capture(image_file, format='jpeg', quality = 20)
        print "  - Image saved:", image_file
        camera.resolution = (100,100)
        thumb_image_file  = "/opt/camera/thumb_%s_%05d.jpg" % (tstmp, self._count)
        cv2.imwrite(thumb_image_file, self.__image0)
        self._count += 1

def process():
    print "Initializing camera..."
    with picamera.PiCamera() as camera:
        camera.rotation = 270
        camera.resolution = (100,100)
        print "Setting focus and light level on camera..."
        time.sleep(2)

        print "Initializing the CameraDetection..."
        detection = MotionDetection()

        count = 0

        while True:
            # Create the in-memory stream
            stream = io.BytesIO()
            camera.capture(stream, use_video_port=True, format='jpeg')

            # Construct a numpy array from the stream
            data = np.fromstring(stream.getvalue(), dtype=np.uint8)
            # "Decode" the image from the array, preserving colour
            image = cv2.imdecode(data, 1)
            if detection.detectMotion(image):
                print "Motion detected"
                detection.saveImage(camera)

            time.sleep(0.2)

if __name__ == "__main__":
    process()
