from picamera.array import PiRGBArray
from picamera import PiCamera
from threading import Thread
import cv2

class PiVideoStreamMono:
    def __init__(self, resolution=(64, 64), framerate=32):
        self.camera = PiCamera()
        self.camera.resolution = resolution
        self.camera.framerate = framerate
        self.rawCapture = PiRGBArray(self.camera, size=resolution)
        self.stream = self.camera.capture_continuous(self.rawCapture,
            format="bgr", use_video_port=True)
        self.frame = None
        self.monoFrame = None
        self.stopped = False

    def start(self):
        Thread(target=self.update, args=(), daemon=True).start()
        return self

    def update(self):
        for f in self.stream:
            self.frame = f.array
            self.rawCapture.truncate(0)
            self.monoFrame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)

            if self.stopped:
                self.stream.close()
                self.rawCapture.close()
                self.camera.close()
                return

    def read(self):
        return self.frame
    
    def readMono(self):
        return self.monoFrame
    
    def stop(self):
        self.stopped = True
