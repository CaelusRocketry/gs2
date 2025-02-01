from channels.generic.websocket import JsonWebsocketConsumer

from ..data.bridge import FSBridge
from ..data.packet import Packet

class GroundConsumer(JsonWebsocketConsumer):
    fsbridge = FSBridge()
    groups = ["ground-station"]

    def connect(self):
        self.accept()
        
    def receive_json(self, content):
        self.send_json(content)
    
    def flight_data(self, message):
        packet = Packet(message["data"])
        if packet.invalid:
            return
        self.send_json(packet.parse())