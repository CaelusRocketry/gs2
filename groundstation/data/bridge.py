from threading import Thread

from groundstation import settings
from .controllers import Controller, XBeeController, SimulationController, BluetoothController

class FSBridge():    
    def __init__(self):
        self.config: dict | None = settings.CONFIG
         
        self.controller: Controller | None = None
        if self.config['environment'] == 'xbee':
            self.controller = XBeeController(self.config)
        elif self.config['environment'] == 'sim':
            self.controller = SimulationController(self.config) 
        elif self.config['environment'] == 'bt':
            self.controller = BluetoothController(self.config)

        self.startup()    

    def startup(self) -> None:
        listen_thread = Thread(name='ListenerThread', target=self.controller.listen, daemon=True)
        listen_thread.start() 