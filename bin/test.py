from Networking import ProtoClient
from Networking.generated.Protobuf.autonomy_pb2 import *

import time

client = ProtoClient(address="localhost", port=8006)


message = AutonomyCommand(enable = True)
client.send_message(message)
print("Sent enable")
time.sleep(2)
message = AutonomyCommand(enable=False)
client.send_message(message)
print("Sent disable")
