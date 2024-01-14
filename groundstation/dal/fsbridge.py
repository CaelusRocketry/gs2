import socket

class FSBridge():
    def __init__(self):
        self.connect_fssocket('127.0.0.1', 5005)
        # print("[FS] FSBridge Initialized")

    def connect_fssocket(self, ip, port):
        # * ported from original ground software
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.socket.bind((ip, port))

        self.socket.listen(1)

        (self.fs, _) = self.socket.accept() # socket connection

    def connect_xbee(self):
        # TODO: connect via xbee since socket is only for simulation
        pass
    