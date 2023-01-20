import udp_server

#TODO: import wrapper_pb3, and perhaps other _pb3 files

class ProtoListener(UdpServer):
    def __init__(self, ip, port, buffer_size=1024):
        self.handlers = {}
        super().__init__(ip, port, buffer_size)

    def handle_message(self, message):
        wrapped_message = wrapper_pb3.WrappedMessage()
        wrapped_message.ParseFromString(message)
        name = wrapped_message.name
        proto = self.handlers[name]["constructor"]()
        proto.ParseFromString(wrapped_message.data)
        self.handlers[name]["handler"](proto)

    def add_handler_and_constructor(self, handler_function, constructor, name):
        self.handlers[name] = {"handler" = handler_function, "constructor" = constructor}