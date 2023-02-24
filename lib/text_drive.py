class TextDrive:
    def send_drive_data(self, throttle, left, right):
        if throttle == 0.0 or (left == 0.0 and right == 0.0):
            print("stop")
            return
        if (left == right):
            if (left > 0.0):
                print("forward")
                return
            else:
                print("backward")
                return
        if (left > 0.0 and right < 0.0):
            print("rotate CW")
            return
        if (left < 0.0 and right > 0.0):
            print("rotate CCW")
            return
        if (left > 0.0):
            if (left > right):
                print("forward skewed left")
                return
            else:
                print("forward skewed right")
                return
        else:
            if (left > right):
                print("backward with right moving faster")
                return
            else:
                print("backward with left moving faster")
                return