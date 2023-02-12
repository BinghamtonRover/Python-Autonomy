import socket

class UdpClient:
    
    def __init__(self, ip, port, buffer_size=1024):
        self.ip = ip
        self.port = port
        self.buffer_size = buffer_size
        self.udp_client_socket = socket.socket(family = socket.AF_INET, type = socket.SOCK_DGRAM)

    def send_message(self, bytes_):
        self.udp_client_socket.sendto(bytes_, (self.ip, self.port))

    def dispose(self):
        self.udp_client_socket.close()