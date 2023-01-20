import socket

class UdpServer:
    
    def __init__(self, ip, port, buffer_size=1024):
        self.ip = ip
        self.port = port
        self.buffer_size = buffer_size
        self.udp_server_socket = socket.socket(family = socket.AF_INET, type = socket.SOCK_DGRAM)
        self.udp_server_socket.bind((self.ip, self.port))
        self.udp_server_socket.settimeout(0.5)

    def start_receiving(self):
        try:
            while(True):
                try:
                    bytes_address_pair = self.udp_server_socket.recvfrom(self.buffer_size)
                    message = bytes_address_pair[0]
                    
                    self.handle_message(message)

                except socket.timeout:
                    pass
        except KeyboardInterrupt:
            self.__exit__('KeyboardInterrupt', None, None)

    def dispose(self):
        self.udp_server_socket.close()

    def handle_message(self, message):
        print(message)