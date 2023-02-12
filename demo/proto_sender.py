import udp_client

#TODO import wrapper_pb3, and perhaps other _pb3 files

class ProtoSender(udp_client.UdpClient):
    def send_proto(self, proto, name):
        wrapped_message = wrapper_pb3.WrappedMessage()
        wrapped_message.data = proto.SerializeToString()
        wrapped_message.name = name
        super.send_message(wrapped_message.SerializeToString())