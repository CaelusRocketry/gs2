from channels.generic.websocket import JsonWebsocketConsumer

from ..dal.fsbridge import FSBridge
from ..dal.packet import Packet


class GroundConsumer(JsonWebsocketConsumer):
    fsbridge = FSBridge()
    groups = ["ground-station"]

    def connect(self):
        self.accept()

    def receive_json(self, content):
        self.send_json(content)

    def flight_data(self, message):
        packet = Packet(message["data"])
        self.send_json(packet.parse())
