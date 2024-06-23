import random
from threading import Thread

from groundstation import settings

from .controllers import Controller, XBeeController, SimulationController
from ..dashboard.models import Test

class FSBridge():    
    def __init__(self):
        self.config: dict | None = settings.CONFIG
         
        self.current_test = self.create_test()

        self.controller: Controller | None = None
        if self.config['environment'] == 'xbee':
            self.controller = XBeeController(self.config, self.current_test)
        elif self.config['environment'] == 'simulation':
            self.controller = SimulationController(self.config, self.current_test) 

        self.startup()    

    def startup(self) -> None:
        listen_thread = Thread(name='ListenerThread', target=self.controller.listen, daemon=True)
        listen_thread.start() 

    def create_test(self):
        test_id = f"{self.config['environment']}-{''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=8))}"
        current_test = Test(test_id=test_id)
        current_test.save()

        return current_test