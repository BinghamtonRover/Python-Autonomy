import gps
import threading

class GPSReader:
    def __init__(self):
        print("gps init")
        self.session = gps.gps("localhost", "2947")
        print("gps stream")
        self.session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)

        self.thread_active = True
        print("gps thread")
        self.reading_thread = threading.Thread(target = self._read_gps, args = ())
        print("starting thread")
        self.reading_thread.start()
        self.lat = 0.0
        self.long = 0.0
        print("done gps setup")

    def __del__(self):
        self.stop_reading()

    def read_gps(self):
        return (self.lat, self.long)

    def stop_reading(self):
        self.thread_active = False

    def _read_gps(self):
        while self.thread_active:
            try:
                gps_data = self.session.next()
                if (gps_data['class'] == 'TPV'):
                    self.lat = gps_data['lat']
                    self.long = gps_data['lon']
            except:
                continue
