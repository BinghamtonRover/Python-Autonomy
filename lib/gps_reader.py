import gps
import threading

class GPSReader:
    def __init__(self):
        self.session = gps.gps("localhost", "2947")
        self.session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)

        self.reading_thread = threading.Thread(target = self._read_gps(), args = ())
        self.reading_thread.start()
        self.lat = 0.0
        self.long = 0.0

    def read_gps(self):
        return (self.lat, self.long)

    def _read_gps(self):
        while True:
            try:
                gps_data = self.session.next()
                if (gps_data['class'] == 'TPV'):
                    self.lat = gps_data['lat']
                    self.long = gps_data['lon']
            except:
                continue
