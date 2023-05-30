import RPi.GPIO as GPIO
import time
import threading

class Ultrasonic:
    def __init__(self):
        self.TRIG_PIN = 27
        self.ECHO_PIN = 22
        self.TRIG_PULSE_WIDTH = 0.000010 # seconds
        self.SAMPLE_PERIOD = 0.1 # seconds

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.TRIG_PIN, GPIO.OUT)
        GPIO.setup(self.ECHO_PIN, GPIO.IN)

        self.trig_time = 0
        self.trig_high = False

        self.echo_time = 0
        self.echo_high = False

        self.run_time = 0
        self.calculating = False
        self.distance = -1.0 # centimeters
        self.blocked = False
        self.previous_distance = -1.0

        self.thread_active = True
        self.reading_thread = threading.Thread(target = self._read_ultrasonic, args = ())
        print("starting thread")
        self.reading_thread.start()

        self.drivable_distance = 90.0

    def is_blocked(self):
        return self.distance < 90.0 and self.previous_distance < 90.0

    def is_drivable(self):
        return self.distance < self.drivable_distance or self.previous_distance < self.drivable_distance

    def _trigger_ultrasonic(self):
        if(self.calculating == True):
            return
        self.calculating = True
        self.trig_high = True
        GPIO.output(self.TRIG_PIN, GPIO.HIGH)
        self.trig_time = time.time()

    def _ultrasonic_events(self):
        GPIO.output(self.TRIG_PIN, GPIO.HIGH)
        self.trig_time = time.time()
        while(True):
            #print("setting trigger high")
            if(time.time() - self.trig_time >= self.TRIG_PULSE_WIDTH):
                break
        GPIO.output(self.TRIG_PIN, GPIO.LOW)
        while(True):
            #print("waiting for echo")
            if(GPIO.input(self.ECHO_PIN) == True):
                break
        self.echo_time = time.time()
        while(True):
            #print("timing echo")
            if(GPIO.input(self.ECHO_PIN) == False):
                break
        self.previous_distance = self.distance
        self.distance = 17000 * (time.time() - self.echo_time)

    def get_distance(self):
        return self.distance

    def stop_reading(self):
        self.thread_active = False

    def _read_ultrasonic(self):
        while self.thread_active:
            current_time = time.time()
            if(current_time - self.run_time >= self.SAMPLE_PERIOD):
                self._trigger_ultrasonic()
                self.run_time = current_time
            self._ultrasonic_events()
        print("stopped reading ultrasonic")

    def clean_up(self):
        GPIO.cleanup()
