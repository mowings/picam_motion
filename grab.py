#!/usr/bin/env python
import io
import time, datetime
import picamera
import cv2
import numpy as np

class MotionDetector:
    def __init__(self, change_threshold, threshold):
        self.images = []
        self._change_threshold = change_threshold
        self._threshold = threshold
        self.motion = None
        self.bitwise_and = None
        self.total=0
        self.mean=0.0
        self.stddev=0.0

    def _ready(self):
        return len(self.images) == 3

    def _new_image(self, image):
        self.images.insert(0, image)
        if len(self.images) > 3: self.images.pop()

    def _get_motion(self):
        if not self._ready(): return None
        diff1 = cv2.absdiff(self.images[1], self.images[0])
        diff2 = cv2.absdiff(self.images[2], self.images[0])
        self.bitwise_and  = cv2.bitwise_and(diff1, diff2)
        dummy, self.motion  =  cv2.threshold(self.bitwise_and, self._threshold, 255, cv2.THRESH_BINARY)
        self.total  = cv2.sumElems(self.motion)[0]
        scalar_mean, scalar_stddev = cv2.meanStdDev(self.motion)
        self.mean = scalar_mean[0][0]
        self.stddev = scalar_stddev[0][0]
        return self.total

    def detect_motion(self, image):
        self._new_image(image)
        total = self._get_motion()
        if total and total > self._change_threshold:
            print "Sum:", self.total
            print "Mean:", self.mean
            print "Std. Dev:", self.stddev
            return True
        else:
            return False

def mk_filename(basename, count):
     return "/opt/camera/motion/%s_%s_%05d.jpg" % (basename, datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S"), count)

def process():
    print "Initializing camera..."
    with picamera.PiCamera() as camera:
        camera.rotation = 270
        camera.resolution = (150,150)
        camera.exposure_mode = 'night'
        camera.awb_mode = 'auto'
        camera.brightness = 60
        camera.color_effect=(128, 128)
        print "Setting focus and light level on camera..."
        time.sleep(2)

        print "Initializing the CameraDetection..."
        detector = MotionDetector(5000, 15)

        count = 0

        while True:
            # Create the in-memory stream
            stream = io.BytesIO()
            camera.capture(stream, use_video_port=True, format='jpeg')

            # Construct a numpy array from the stream
            data = np.fromstring(stream.getvalue(), dtype=np.uint8)
            # "Decode" the image from the array, preserving colour
            image = cv2.imdecode(data, cv2.CV_LOAD_IMAGE_GRAYSCALE)
            if detector.detect_motion(image):
                image_file =  mk_filename('motion', count)
                cv2.imwrite(image_file, detector.motion)
                image_file =  mk_filename('frame', count)
                cv2.imwrite(image_file, detector.images[1])
                image_file = mk_filename('mask', count)
                cv2.imwrite(image_file, detector.bitwise_and)
                print "Motion detected. Frame: ", count
                print "    Sum:", detector.total
                print "    Mean:", detector.mean
                print "    Std. Dev:", detector.stddev
     
                count += 1

if __name__ == "__main__":
    process()
