import socket
import bluetooth
import traceback

from time import sleep, time

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

        if packet.invalid:
            return
        
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
        current_test = Test.objects.create(
            environment=self.config['environment']
        )
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
        self.timeout = self.config["telemetry"]["sim"]["timeout"]
        self.max_retries = self.config["telemetry"]["sim"]["max_retries"]

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.socket.bind((self.host, self.port))

    def listen(self) -> None: 
        listening = False
        first_time_listen = True
        
        while True:
            if not first_time_listen:
                self.socket.settimeout(self.timeout)
                retry_count = 0
                while retry_count < self.max_retries:
                    try:
                        self.socket.listen(1)
                        self.fs, _ = self.socket.accept()
                        break
                    except socket.timeout:
                        retry_count += 1
                if retry_count >= self.max_retries:
                    break
            else:
                self.socket.listen(1)
                self.fs, _ = self.socket.accept()  # addr doesn't matter
                self.socket.settimeout(self.timeout)
            
            first_time_listen = False
            listening = True
            retry_count = 0

            while listening:
                try:
                    data: str = self.fs.recv(self.bufsize).decode()
                    
                    if len(data) == 0:
                        # client disconnected
                        listening = False
                        break

                    if not self.current_test:
                        self.current_test = self.create_test()
                    self.store_packet(data, self.current_test)

                    async_to_sync(self.channel_layer.group_send)("ground-station", {
                        "type": "flight.data",
                        "data": data
                    })
                except socket.timeout:
                    if retry_count < self.max_retries:
                        retry_count += 1
                    else:
                        listening = False
                except socket.error:
                    listening = False

                sleep(self.delay)
            
            self.fs.close()
            # don't try retrying again 
            if retry_count >= self.max_retries:
                break
            sleep(self.delay)
        
        if self.current_test:
            self.current_test.completed = True
            self.current_test.save()
            self.current_test = None

class XBeeController(Controller):
    def __init__(self, config: dict):
        super().__init__(config)

        self.current_test = None
        self.channel_layer = get_channel_layer()
        self.baud = self.config["telemetry"]["xbee"]["baudrate"]
        self.port = self.config["telemetry"]["xbee"]["port"]
        self.delay = self.config["telemetry"]["xbee"]["delay"]
        self.timeout = self.config["telemetry"]["xbee"]["timeout"]
        self.max_retries = self.config["telemetry"]["xbee"]["max_retries"]

        self.xbee = XBeeDevice(self.port, self.baud)

    def listen(self) -> None:
        self.xbee.open(force_settings=True)
        
        retry_count = 0
        last_message_time = None
        listening = True

        while listening:
            msg: XBeeMessage | None = self.xbee.read_data()

            if msg is not None:
                data = msg.data.decode()
                last_message_time = time()

                if not self.current_test:
                    self.current_test = self.create_test()
                self.store_packet(data, self.current_test)

                async_to_sync(self.channel_layer.group_send)("ground-station", {
                    "type": "flight.data",
                    "data": data
                })
            elif last_message_time is not None and time() - last_message_time >= self.timeout and retry_count < self.max_retries:
                retry_count += 1
                last_message_time = time()
            else:
                listening = False
                if self.current_test:
                    self.current_test.completed = True
                    self.current_test.save()
                    self.current_test = None

            sleep(self.delay)
        
        if self.xbee.is_open():
            self.xbee.close()

class BluetoothController(Controller):
    def __init__(self, config: dict):
        super().__init__(config)

        self.current_test = None
        self.channel_layer = get_channel_layer()
        self.device_name = self.config["telemetry"]["bt"]["name"]
        self.bufsize = self.config["telemetry"]["bt"]["bufsize"]
        self.delay = self.config["telemetry"]["bt"]["delay"]
        self.timeout = self.config["telemetry"]["bt"]["timeout"]
        self.max_retries = self.config["telemetry"]["bt"]["max_retries"]

        self.host = None
        self.port = None

        self.socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

    def find_bt_device(self):
        print("\nSearching for Bluetooth devices...")
        nearby_devices = bluetooth.discover_devices(lookup_names=True)

        for addr, name in nearby_devices:
            print(addr, name)
            if name == self.device_name:
                print(f"Found device {name} with address {addr}")
                self.host = addr
                break

        if self.host is None:
            print(f"Could not find device with name {self.device_name}.")
            return

        service = bluetooth.find_service(address=self.host)[0]
        self.port = service["port"]

        print(f"Using {service['name']} at {service['host']} on port {service['port']}.")

    def listen(self) -> None:
        listening = False
        first_time_listen = True

        while True:
            while self.port is None:
                self.find_bt_device()
                sleep(1)

            if not first_time_listen:
                print("Retrying connection...")
                self.socket.settimeout(self.timeout)
                retry_count = 0
                while retry_count < self.max_retries:
                    try:
                        self.socket.connect((self.host, self.port))
                        break
                    except bluetooth.BluetoothError as e:
                        print(traceback.format_exc())
                        retry_count += 1
                        sleep(self.delay)
                if retry_count >= self.max_retries:
                    break
            else:
                self.socket.connect((self.host, self.port))
                self.socket.settimeout(self.timeout)

            first_time_listen = False
            listening = True
            retry_count = 0

            while listening:
                try:
                    data: str = self.socket.recv(self.bufsize).decode()
                    
                    if len(data) == 0:
                        # device disconnected
                        listening = False
                        break

                    if not self.current_test:
                        self.current_test = self.create_test()
                    self.store_packet(data, self.current_test)

                    async_to_sync(self.channel_layer.group_send)("ground-station", {
                        "type": "flight.data",
                        "data": data
                    })
                except bluetooth.BluetoothError:
                    print(traceback.format_exc())
                    if retry_count < self.max_retries:
                        retry_count += 1
                    else:
                        listening = False
                except Exception:
                    print(traceback.format_exc())
                    listening = False

                sleep(self.delay)
            
            print("\nDevice disconnected.")

            self.socket.close()
            if retry_count >= self.max_retries:
                break
            sleep(self.delay)

        if self.current_test:
            self.current_test.completed = True
            self.current_test.save()
            self.current_test = None
