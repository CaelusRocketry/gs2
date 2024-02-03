from channels.generic.websocket import JsonWebsocketConsumer
from groundstation.dal.fsbridge import FSBridge

class GroundConsumer(JsonWebsocketConsumer):
    fsbridge = FSBridge()
    groups = ["ground-station"]

    def connect(self):
        self.accept()

    def receive_json(self, content):
        self.send_json(content)
    
    def flight_data(self, message):
        packet = message['data']
        packet = packet[1:-1] # remove ^ & $
        content = self.parse_packet(packet)
        self.send_json(content)
        
    def parse_packet(self, packet):
        tokens = packet.split("|")
        header = tokens[0]
        message = tokens[2]

        return {
            "header": header,
            "message": message
        }

