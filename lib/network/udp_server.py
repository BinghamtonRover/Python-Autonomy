import socket

class UdpServer:
    
    def __init__(self, ip, port, buffer_size=1024):
        self.ip = ip
        self.port = port
        self.buffer_size = buffer_size

    def start_receiving(self):
        try:
            while(True):
                try:
                    bytes_address_pair = self.udp_server_socket.recvfrom(self.buffer_size)
                    message = bytes_address_pair[0]
                    address = bytes_address_pair[1]
                    
                    self.handle_message(message)

                    # Potentially to be removed
                    self.return_message()

                except socket.timeout:
                    pass
        except KeyboardInterrupt:
            self.__exit__('KeyboardInterrupt', None, None)

    def __enter__(self):
        self.udp_server_socket = socket.socket(family = socket.AF_INET, type = socket.SOCK_DGRAM)
        self.udp_server_socket.bind((self.ip, self.port))
        self.udp_server_socket.settimeout(0.5)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.udp_server_socket.close()

    def get_socket(self):
        return self.udp_server_socket

    def return_message(self):
        self.udp_server_socket.sendto(str.encode('Message Received'), address)

    def handle_message(self, message):
        print(message)