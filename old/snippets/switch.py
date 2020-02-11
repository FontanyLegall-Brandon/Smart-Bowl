import time
import grovepi

# Connect the Grove Button to digital port D3
# SIG,NC,VCC,GND
button = 2
print("toto")
grovepi.pinMode(button,"INPUT")
print("test")
i = 0
while True:

    if grovepi.digitalRead(button) == 1 and not pressed:
        i += 1
        print(i)
        pressed = True

    if grovepi.digitalRead(button) == 0 :
        pressed = False