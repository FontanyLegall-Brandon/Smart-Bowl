import grove_i2c_motor_driver
import switch
import time
import smbus2 as smbus

class Motor:
    motor = None
    con = False
    switch = None

    def __init__(self):
        self.switch = switch.Switch()

        while not self.con:
            print("NO CONN MAIN")
            time.sleep(1)
            try:
                self.motor = grove_i2c_motor_driver.motor_driver(address=0x0a)
                self.motor.MotorSpeedSetAB(100, 100)
            except IOError:
                continue
            self.con = True
            self.bus = smbus.SMBus(1)

        self.close()

        # Set motor direction
    def MotorDirectionSet(self, Direction):
        # use the bus that matches your raspi version
        self.bus.write_i2c_block_data(0x0a, 0xaa, [Direction, 0])
        time.sleep(0.01)

    def step(self, dir, steps):


        self.motor.MotorSpeedSetAB(100, 100)

        for i in range(steps // 4):
            self.MotorDirectionSet(0b0001)
            self.MotorDirectionSet(0b0101)
            self.MotorDirectionSet(0b0100)
            self.MotorDirectionSet(0b0110)
            self.MotorDirectionSet(0b0010)
            self.MotorDirectionSet(0b1010)
            self.MotorDirectionSet(0b1000)
            self.MotorDirectionSet(0b1001)

    def open(self):
        self.step('CLK', 200)

    def close(self):
        turned = False
        while not self.switch.isPressed():
            turned = True
            self.step('CLK', 8)
        # Little rotation to apply to completely close bowl
        if turned:
            self.step('CLK', 4)
        self.motor.MotorSpeedSetAB(0, 0)


if __name__ == "__main__":
    tryMotor = Motor()
    #tryMotor.open()