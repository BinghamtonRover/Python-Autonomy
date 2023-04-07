import gps

class GPSReader:
    def __init__:
        self.session = gps.gps("localhost", "2947")
        self.session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)

    def read_gps():
        try:
            gps_reading = self.session.next()
            return (gps_reading['lat'], gps_reading['lon'])
        except:
            return None
