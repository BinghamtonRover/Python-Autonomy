import RPi.GPIO as GPIO
import time

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

        self.thread_active = True
        self.reading_thread = threading.Thread(target = self._read_ultrasonic, args = ())
        print("starting thread")
        self.reading_thread.start()

    def _trigger_ultrasonic(self):
        if(self.calculating == True):
            return
        self.calculating = True
        self.trig_high = True
        GPIO.output(self.TRIG_PIN, GPIO.HIGH)
        self.trig_time = time.time()

    def _ultrasonic_events(self):
        if(self.trig_high == True):
            if(time.time() - self.trig_time >= self.TRIG_PULSE_WIDTH):
                GPIO.output(self.TRIG_PIN, GPIO.LOW)
                self.trig_high = False
        elif(GPIO.input(self.ECHO_PIN) == True and self.echo_high == False):
            self.echo_high = True
            self.echo_time = time.time()
        elif(self.echo_high == True):
            if(GPIO.input(self.ECHO_PIN) == False):
                self.calculating = False
                self.echo_high = False
                self.distance = 17000(time.time() - self.echo_time)

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

    def clean_up(self):
        GPIO.cleanup()