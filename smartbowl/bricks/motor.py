import grove_i2c_motor_driver
import switch
import time
class Motor:
    motor = None
    con = False
    switch = None

    def __init__(self):
        self.switch = switch.Switch()
        while not self.con:
            print("NO CONN")
            time.sleep(1)
            try:
                self.motor = grove_i2c_motor_driver.motor_driver(address=0x0f)
                self.motor.MotorSpeedSetAB(100, 100)
            except IOError:
                continue
            self.con = True
        while not self.switch.isPressed():
            print(self.switch.isPressed())

            self.step('CLK', 4)
        self.motor.MotorSpeedSetAB(0, 0)

    def interstep(self):
        time.sleep(0.001)

    def step(self, dir, steps):


        self.motor.MotorSpeedSetAB(100, 100)

        for i in range(steps // 4):
            self.motor.MotorDirectionSet(0b0001)
            self.motor.MotorDirectionSet(0b0101)
            self.motor.MotorDirectionSet(0b0100)
            self.motor.MotorDirectionSet(0b0110)
            self.motor.MotorDirectionSet(0b0010)
            self.motor.MotorDirectionSet(0b1010)
            self.motor.MotorDirectionSet(0b1000)
            self.motor.MotorDirectionSet(0b1001)
            self.interstep()

        #self.motor.MotorSpeedSetAB(0, 0)
        #self.motor.MotorDirectionSet(0b0001)

    def open(self):
        self.step('CLK', 400)

    def close(self):
        self.step('CLK', 400)


if __name__ == "__main__":
    tryMotor = Motor()
    #tryMotor.open()