import grovepi

class Switch:
    button = 3

    def isPressed(self):
        return grovepi.digitalRead(self.button) == 1

if __name__ == "__main__":
    trySwitch = Switch()
    i = 0
    while True:
        if trySwitch.isPressed():
            i += 1
            print(i)