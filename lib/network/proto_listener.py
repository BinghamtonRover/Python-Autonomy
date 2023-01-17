import udp_server

#TODO: import wrapper_pb3, and perhaps other _pb3 files

class ProtoListener(UdpServer):
    def __init__(self, ip, port, buffer_size=1024):
        self.handlers = {}
        super().__init__(ip, port, buffer_size)

    def handle_message(self, message):
        wrapped_message = wrapper_pb3.WrappedMessage()
        wrapped_message.ParseFromString(message)
        #TODO: proto = ..._pb3....Message(), depends on the type of message and the file in which the message is defined
        proto.ParseFromString(wrapped_message.data)
        name = wrapped_message.name
        if name in self.handlers.keys():
            self.handlers[name](proto)
        else:
            print('This proto listener does not have a handler for a {name} message.')

    def add_handler(self, func, name):
        self.handlers[name] = func