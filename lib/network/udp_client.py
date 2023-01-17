import socket

class UdpClient:
    
    def __init__(self, ip, port, buffer_size=1024):
        self.ip = ip
        self.port = port
        self.buffer_size = buffer_size

    def send_message(self, bytes_):
        self.udp_client_socket.sendto(bytes_, (self.ip, self.port))
        msg_from_server = self.udp_client_socket.recvfrom(self.buffer_size)
        self.receive_message(msg_from_server)

    def __enter__(self):
        self.udp_client_socket = socket.socket(family = socket.AF_INET, type = socket.SOCK_DGRAM)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.udp_client_socket.close()

    def get_socket(self):
        return self.udp_client_socket

    def receive_message(self, message):
        print(msg_from_server)