import socket
import threading

from asgiref.sync import async_to_sync
from channels.consumer import SyncConsumer

class FSBridge(SyncConsumer):    
    def __init__(self):
        listener = threading.Thread(target=self.listen_fssocket, daemon=True)
        listener.start()

    def startup(self, message):
        print("[FS] Starting up bridge...")

    def connect_xbee(self):
        # TODO: connect via xbee since socket is only for simulation
        pass

    def listen_fssocket(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.socket.bind(("127.0.0.1", 5005))

        self.socket.listen(1)

        (self.fs, _) = self.socket.accept() # socket connection

        while True:
            data = self.fs.recv(8192).decode()
            async_to_sync(self.channel_layer.group_send)("ground-station", {
                "type": "flight.data",
                "data": data
            })            
