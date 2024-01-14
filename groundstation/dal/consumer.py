import json

from channels.generic.websocket import WebsocketConsumer
from groundstation.dal.fsbridge import FSBridge

class DataConsumer(WebsocketConsumer):
    fsbridge = FSBridge()

    def connect(self):
        self.accept()
    
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['data']
        self.send(text_data=json.dumps({
            'data': message
        }))