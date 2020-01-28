# GrovePi + Grove Ultrasonic Ranger from grovepi import *
# Connect the Grove Ultrasonic Ranger to digital port D4 # SIG,NC,VCC,GND

from grovepi import *
# Connect the Grove Ultrasonic Ranger to digital port D4 # SIG,NC,VCC,GND

class Supersonic:
    ultrasonic_ranger = 4

    def detect(self):
        try:
            # Read distance value from Ultrasonic
            return ultrasonicRead(self.ultrasonic_ranger)
        except TypeError:
            print "Error"
        except IOError:
            print "Error"

if __name__ == "__main__":
    sensor = Supersonic()
    while True:
        print(sensor.detect())