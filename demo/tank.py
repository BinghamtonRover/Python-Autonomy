#import pigpio
import time

class Tank:
	LEFT_MOTOR_PIN = 12
	RIGHT_MOTOR_PIN = 19

	PWM_FREQUENCY = 50
	PWM_MAX_POS = 82500
	PWM_MIN_POS = 76500
	PWM_ZERO = 75000
	PWM_MIN_NEG = 73500
	PWM_MAX_NEG = 67500
	PWM_RANGE = PWM_MAX_POS - PWM_MAX_NEG

	VEL_MAX_NEG = -10.0
	VEL_MED_NEG = -5.0
	VEL_ZERO = 0.0
	VEL_MAX_POS = 10.0
	VEL_MED_POS = 5.0

	gpio = None
	
	def __init__(self):
		self.initialize_tank()

	def initialize_tank(self):
		global gpio
		#gpio = pigpio.pi()
		
	def set_left_velocity(self, velocity):
		PWM = 0
		if (velocity == 0):
			PWM = self.PWM_ZERO
			#gpio.hardware_PWM(int(LEFT_MOTOR_PIN), int(PWM_FREQUENCY), int(PWM))
		elif (velocity > 0):
			if (velocity > self.VEL_MAX_POS):
				velocity = self.VEL_MAX_POS
			PWM = (self.PWM_MIN_POS + velocity * (self.PWM_MAX_POS - self.PWM_MIN_POS) / (self.VEL_MAX_POS - self.VEL_ZERO))
			#gpio.hardware_PWM(int(LEFT_MOTOR_PIN), int(PWM_FREQUENCY), int(PWM))
		else:
			if (velocity < self.VEL_MAX_NEG):
				velocity = self.VEL_MAX_NEG
			PWM = (self.PWM_MIN_NEG + velocity * (self.PWM_MAX_NEG - self.PWM_MIN_NEG) / (self.VEL_MAX_NEG - self.VEL_ZERO))
			#gpio.hardware_PWM(int(LEFT_MOTOR_PIN), int(PWM_FREQUENCY), int(PWM))
		
	def set_right_velocity(self, velocity):
		PWM = 0
		if (velocity == 0):
			PWM = self.PWM_ZERO
			#gpio.hardware_PWM(int(RIGHT_MOTOR_PIN), int(PWM_FREQUENCY), int(PWM))
		elif (velocity > 0):
			if (velocity > self.VEL_MAX_POS):
				velocity = self.VEL_MAX_POS
			PWM = (self.PWM_MIN_POS + velocity * (self.PWM_MAX_POS - self.PWM_MIN_POS) / (self.VEL_MAX_POS - self.VEL_ZERO))
			#gpio.hardware_PWM(int(RIGHT_MOTOR_PIN), int(PWM_FREQUENCY), int(PWM))
		else:
			if (velocity < VEL_MAX_NEG):
				velocity = VEL_MAX_NEG
			PWM = (self.PWM_MIN_NEG + velocity * (self.PWM_MAX_NEG - self.PWM_MIN_NEG) / (self.VEL_MAX_NEG - self.VEL_ZERO))
			#gpio.hardware_PWM(int(RIGHT_MOTOR_PIN), int(PWM_FREQUENCY), int(PWM))

