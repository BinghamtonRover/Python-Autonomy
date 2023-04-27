from lib.imu.osc_decoder import *
import socket
import time
import threading

class Imu: 

    def __init__(self): 
        self.x = 0
        self.y = 0
        self.z = 0

        # Send /identify message to strobe all LEDs.  The OSC message is constructed
        # from raw bytes as per the OSC specification.  The IP address must be equal to
        # the IP address of the target NGIMU.
        self.send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Array of UDP ports to listen to, one per NGIMU.  These ports must be equal to
        # the UDP Send Port in the NGIMU settings.  The UDP Send IP Address setting
        # must be the computer's IP address.  Both these settings are changed
        # automatically when connecting to the NGIMU using the NGIMU GUI.
        self.receive_ports = [8007, 8010, 8011, 8012, 8232]
        self.receive_sockets = [socket.socket(socket.AF_INET, socket.SOCK_DGRAM) for _ in range(len(self.receive_ports))]

        index = 0
        for receive_socket in self.receive_sockets:
            receive_socket.bind(("", self.receive_ports[index]))
            index = index + 1
            receive_socket.setblocking(False)

        self.send_socket.sendto(bytes("/identify\0\0\0,\0\0\0", "utf-8"), ("192.168.1.232", 9000))

        self.thread_active = True
        self._start_reading_thread()

    def __del__(self):
        self.stop_reading()

    def _start_reading_thread(self):
        reading_thread = threading.Thread(target = self._read_imu, args = ())
        reading_thread.start()

    #set values
    def _handle_message(self, message):
        name = message[1]
        if name != "/euler":
            return

        self.x = message[2]
        self.y = message[3]
        self.z = (message[4])


    def get_orientation(self):
        #while True:
        #    for udp_socket in self.receive_sockets:
        #        try:
        #            data, addr = udp_socket.recvfrom(2048)
        #        except socket.error: break
        #        else:
        #            for message in osc_decoder.decode(data):
        #                # print(udp_socket.getsockname(), message)
        #                # print(message)
        #                print(message)
        #                self._handle_message(message)

        return (self.x, self.y, self.z)

    def stop_reading(self):
        self.thread_active = False

    def _read_imu(self):
        while self.thread_active:
            for udp_socket in self.receive_sockets:
                try:
                    data, addr = udp_socket.recvfrom(2048)
                except socket.error: pass
                else:
                    for message in decode(data):
                        # print(udp_socket.getsockname(), message)
                        # print(message)
                        self._handle_message(message)
        print("stopped reading")


