import grove_i2c_motor_driver
import switch
import time
import smbus2 as smbus

class MotorDropper :
    motor = None
    con = False
    switch = None

    def __init__(self):
        self.switch = switch.Switch()
        while not self.con:
            print("NO CONN DROPPER")
            time.sleep(2)
            try:
                self.motor = grove_i2c_motor_driver.motor_driver(address=0x0f)
                self.motor.MotorSpeedSetAB(100, 100)
            except IOError:
                continue
            self.con = True
        self.motor.MotorSpeedSetAB(0, 0)
        self.bus = smbus.SMBus(1)

    def interstep(self):
        time.sleep(0.001)

    def MotorDirectionSet(self, Direction):
        # use the bus that matches your raspi version
        self.bus.write_i2c_block_data(0x0f, 0xaa, [Direction, 0])
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

    def drop(self):
        self.step('CLK', 400)
        time.sleep(1)


if __name__ == "__main__":
    tryMotor = MotorDropper()
    #tryMotor.open()