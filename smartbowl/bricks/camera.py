import time
import base64
import subprocess

class Camera:
    current_milli_time = lambda self: int(round(time.time() * 1000))

    def raspistillCapture(self, out):
        p = subprocess.Popen('raspistill -w 500 -h 281 -o %s' % out, shell=True)
        p.wait()

    def capture(self):
        imageName = '/tmp/image_%s.jpg' % self.current_milli_time()
        self.raspistillCapture(imageName)

        return imageName

    def encode(self, imageName):
        with open(imageName, "rb") as image_file:
            return base64.b64encode(image_file.read())

if __name__ == "__main__":
    cam = Camera()
    imageName = cam.capture()
    print(imageName)