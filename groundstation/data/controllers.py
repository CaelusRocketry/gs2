import socket
from time import sleep

from digi.xbee.devices import XBeeDevice
from digi.xbee.reader import XBeeMessage
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .packet import Packet
from ..dashboard.models import Test, StoredPacket

class Controller:
    def __init__(self, config: dict, environment: str):
        self.config = config
        self.environment = environment

    def store_packet(self, pkt: str, current_test: Test):
        packet = Packet(pkt)
        
        if self.config[self.environment]['format'] == 'parsed':
            payload: dict = packet.parse()['payload']
        else:
            payload = { 'data': packet.data }
        
        StoredPacket.objects.create(
            header=packet.header,
            timestamp=packet.timestamp,
            values=payload,
            test=current_test
        )

class SimulationController(Controller):
    def __init__(self, config: dict, current_test: Test):
        super().__init__(config, "sim")
        
        self.current_test = current_test
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
            
            if data.startswith("^") and data.endswith("$"):
                if data[1:4] != "DAT" and data[1:4] != "VDT":
                    continue
            else:
                continue

            self.store_packet(data, self.current_test)
            
            async_to_sync(self.channel_layer.group_send)("ground-station", {
                "type": "flight.data",
                "data": data
            })
            
            sleep(self.delay)

class XBeeController(Controller):
    def __init__(self, config: dict, current_test: Test):
        super().__init__(config, "xbee")

        self.current_test = current_test
        self.channel_layer = get_channel_layer()
        self.baud = self.config["telemetry"]["xbee"]["baudrate"]
        self.port = self.config["telemetry"]["xbee"]["port"]
        self.delay = self.config["telemetry"]["xbee"]["delay"]
        
        self.xbee = XBeeDevice(self.port, self.baud)
        
    def listen(self) -> None:
        self.xbee.open()

        self.listening = True

        while self.listening:
            msg: XBeeMessage = self.xbee.read_data()

            if not msg is None:
                data = msg.data.decode()

                self.store_packet(data, self.current_test)

                async_to_sync(self.channel_layer.group_send)("ground-station", {
                    "type": "flight.data",
                    "data": data
                })
            
            sleep(self.delay)