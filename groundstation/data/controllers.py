import socket
import serial
from time import sleep

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class SimulationController():
    def __init__(self, config: dict):
        self.config = config
        self.channel_layer = get_channel_layer()
        self.host = self.config["telemetry"]["sim"]["host"]
        self.port = self.config["telemetry"]["sim"]["port"]
        self.bufsize = self.config["telemetry"]["sim"]["bufsize"]
        self.delay = self.config["telemetry"]["sim"]["delay"]

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.socket.bind((self.host, self.port))

    def thread(self) -> None: 
        self.socket.listen(1)
        (self.fs, _) = self.socket.accept() # addr doesn't matter

        self.listening = True

        while self.listening:
            data: str = self.fs.recv(self.bufsize).decode()
            async_to_sync(self.channel_layer.group_send)("ground-station", {
                "type": "flight.data",
                "data": data
            })
            sleep(self.delay)
    
    def send_data(self, message: str) -> None:
        self.fs.send(message)

class XBeeController():
    def __init__(self, config: dict):
        self.config = config
        self.channel_layer = get_channel_layer()
        self.baud = self.config["telemetry"]["xbee"]["baudrate"]
        self.port = self.config["telemetry"]["xbee"]["port"]
        self.delay = self.config["telemetry"]["xbee"]["delay"]
        
        # we use serial here instead of digi-xbee since the latter only   
        # works with API mode and it would be much simpler to use AT mode
        self.xbee = serial.Serial(self.port, self.baud)
        self.xbee.reset_input_buffer()
        
    def thread(self) -> None:
        self.listening = True

        while self.listening:
            data: str = self.xbee.read(self.xbee.in_waiting).decode()
            async_to_sync(self.channel_layer.group_send)("ground-station", {
                "type": "flight.data",
                "data": data
            })
            sleep(self.delay)

    def send_data(self, message: str) -> None:
        # TODO: possibly thread this
        self.xbee.write(message.encode())