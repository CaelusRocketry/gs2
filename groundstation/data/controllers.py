import socket
import random
from time import sleep

from digi.xbee.devices import XBeeDevice
from digi.xbee.models.message import XBeeMessage
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .packet import Packet
from ..dashboard.models import Test, StoredPacket

class Controller:
    def __init__(self, config: dict):
        self.config = config
        
    def store_packet(self, pkt: str, current_test: Test):
        packet = Packet(pkt)
        
        if self.config['telemetry'][self.config['environment']]['store'] == 'parsed':
            payload: dict = packet.parse()['payload']
        else:
            payload = { 'data': packet.data }
        
        StoredPacket.objects.create(
            header=packet.header,
            timestamp=packet.timestamp,
            values=payload,
            test=current_test
        )

    def create_test(self):
        test_id = f"{self.config['environment']}-{''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=8))}"
        current_test = Test(test_id=test_id)
        current_test.save()
        
        return current_test

class SimulationController(Controller):
    def __init__(self, config: dict):
        super().__init__(config)
        
        self.current_test = None
        self.channel_layer = get_channel_layer()
        self.host = self.config["telemetry"]["sim"]["host"]
        self.port = self.config["telemetry"]["sim"]["port"]
        self.bufsize = self.config["telemetry"]["sim"]["bufsize"]
        self.delay = self.config["telemetry"]["sim"]["delay"]

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.socket.bind((self.host, self.port))

    def listen(self) -> None: 
        self.socket.listen(1)
        (self.fs, _) = self.socket.accept() # addr doesn't matter

        self.listening = True

        while self.listening:
            data: str = self.fs.recv(self.bufsize).decode()

            if not self.current_test:
                self.current_test = self.create_test()
            self.store_packet(data, self.current_test)

            async_to_sync(self.channel_layer.group_send)("ground-station", {
                "type": "flight.data",
                "data": data
            })
            
            sleep(self.delay)

class XBeeController(Controller):
    def __init__(self, config: dict):
        super().__init__(config)

        self.current_test = None
        self.channel_layer = get_channel_layer()
        self.baud = self.config["telemetry"]["xbee"]["baudrate"]
        self.port = self.config["telemetry"]["xbee"]["port"]
        self.delay = self.config["telemetry"]["xbee"]["delay"]
        
        self.xbee = XBeeDevice(self.port, self.baud)

    def listen(self) -> None:
        self.xbee.open(force_settings=True)
        
        self.listening = True

        while self.listening:
            msg: XBeeMessage = self.xbee.read_data()

            if not msg is None:
                data = msg.data.decode()

                if not self.current_test:
                    self.current_test = self.create_test()
                self.store_packet(data, self.current_test)

                async_to_sync(self.channel_layer.group_send)("ground-station", {
                    "type": "flight.data",
                    "data": data
                })
            
            sleep(self.delay)