from lib.ultrasonic import Ultrasonic
import time

def main():
    ultrasonic = Ultrasonic()
    while True:
        print(ultrasonic.get_distance())
        time.sleep(0.5)

if __name__ == "__main__":
    main()
