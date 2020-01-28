import grovepi

class Switch:
    button = 2

    def isPressed(self):
        return grovepi.digitalRead(self.button) == 1