from channels.generic.websocket import AsyncJsonWebsocketConsumer
from groundstation.dal.fsbridge import FSBridge

class GroundConsumer(AsyncJsonWebsocketConsumer):
    groups = ["ground-station"]

    def __init__(self):
        super().__init__()
        self.bridge_connect = False

    async def connect(self):
        if not self.bridge_connect:
            await self.channel_layer.send("flight-software", {
                "type": "startup"
            })
            self.bridge_connect = True
        await self.accept()

    async def receive_json(self, content):
        await self.send_json(content)
    
    async def flight_data(self, message):
        packet = message['data']
        packet = packet[1:-1] # remove ^ & $
        content = self.parse_packet(packet)
        await self.send_json(content)
        
    def parse_packet(self, packet):
        tokens = packet.split("|")
        header = tokens[0]
        message = tokens[2]

        return {
            "header": header,
            "message": message
        }

