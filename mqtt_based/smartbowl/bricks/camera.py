from picamera import PiCamera
from time import sleep
import time
import base64

class Camera:
    current_milli_time = lambda self: int(round(time.time() * 1000))
    camera = None

    def __init__(self):
        self.camera = PiCamera()

    def capture(self):
        imageName = '/tmp/image_%s.jpg' % self.current_milli_time()
        self.camera.start_preview()
        sleep(5)
        self.camera.capture(imageName)
        self.camera.stop_preview()

        return imageName

    def send(self, imageName, mqtt):
        with open("yourfile.ext", "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read())
            mqtt.publish('picture', encoded_image)
            print encoded_image
            print "image %s send" % imageName


if __name__ == "__main__":
    cam = Camera()
    imageName = cam.capture()
    print imageName