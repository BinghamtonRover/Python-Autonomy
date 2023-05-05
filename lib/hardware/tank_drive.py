import pigpio
import time

from network.generated import DriveCommand

LEFT_MOTOR_PIN = 13
RIGHT_MOTOR_PIN = 12

PWM_FREQUENCY = 50
PWM_MAX_POS = 82500
PWM_MIN_POS = 76500
PWM_ZERO = 75000
PWM_MIN_NEG = 73500
PWM_MAX_NEG = 67500
PWM_RANGE = PWM_MAX_POS - PWM_MAX_NEG

VEL_MAX_NEG = -1.0 # -10.0
VEL_MED_NEG = -0.5 #-5.0
VEL_ZERO = 0.0
VEL_MAX_POS = 1.0 #10.0
VEL_MED_POS = 0.5 #5.0

class TankDrive: 
    def __init__(self): 
        self.gpio = pigpio.pi()
        if self.gpio.connected:
            print("Tank successfully initialized")
        else:
            print("[Error] PiGPIO is not running")
            quit()
        self.throttle = 0
        self.left_velocity = 0
        self.right_velocity = 0

    def handle_command(self, command: DriveCommand):
        if command.set_throttle: self.throttle = command.throttle
        if command.set_left: self.left_velocity = command.left
        if command.set_right: self.right_velocity = command.right
        self.update_motors()

    def update_motors(self): 
        # Writes commands to the ESC
        #print(f"Writing throttle={self.throttle}, left={self.left_velocity}, right={self.right_velocity}")
        self.set_velocity(LEFT_MOTOR_PIN, self.left_velocity)
        self.set_velocity(RIGHT_MOTOR_PIN, self.right_velocity)

    def set_velocity(self, pin, velocity): 
        velocity = -velocity
        pwm = 0
        if velocity == 0: pwm = PWM_ZERO
        elif velocity > 0:
            if velocity > VEL_MAX_POS: velocity = VEL_MAX_POS
            pwm = (PWM_MIN_POS + velocity * (PWM_MAX_POS - PWM_MIN_POS) / (VEL_MAX_POS - VEL_ZERO))
        elif velocity < 0: 
            if (velocity < VEL_MAX_NEG): velocity = VEL_MAX_NEG
            pwm = (PWM_MIN_NEG + velocity * (PWM_MAX_NEG - PWM_MIN_NEG) / (VEL_MAX_NEG - VEL_ZERO))
        self.gpio.hardware_PWM(pin, PWM_FREQUENCY, int(pwm))

    def set_throttle(self, throttle):
        self.throttle = throttle
        self.update_motors()

