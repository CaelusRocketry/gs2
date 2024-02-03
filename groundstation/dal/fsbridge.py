import socket
from time import sleep
from threading import Thread

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

class FSBridge():    
    def __init__(self):
        self.channel_layer = get_channel_layer()
        self.startup()
    
    def startup(self):
        listener = Thread(target=self.listen_fssocket, daemon=True)
        self.listening = True
        listener.start() 

    def listen_xbee(self) -> None:
        # TODO: connect via xbee since socket is only for simulation
        pass

    def listen_fssocket(self) -> None:
        skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        skt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        skt.bind(("127.0.0.1", 5005))

        skt.listen(1)

        (self.fs, _) = skt.accept()

        while self.listening:
            data: str = self.fs.recv(8192).decode()
            async_to_sync(self.channel_layer.group_send)("ground-station", {
                "type": "flight.data",
                "data": data
            })
            sleep(0.1)