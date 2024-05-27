from threading import Thread
import json

from groundstation import settings

from .controllers import XBeeController, SimulationController


class FSBridge:
    def __init__(self):
        self.config_file: str = settings.CONFIG
        with open(self.config_file) as f:
            self.config: dict = json.load(f)

        self.controller: XBeeController | SimulationController | None = None
        if self.config["environment"] == "xbee":
            self.controller = XBeeController(self.config)
        elif self.config["environment"] == "simulation":
            self.controller = SimulationController(self.config)

        self.startup()

    def startup(self) -> None:
        listen_thread = Thread(name="ListenerThread", target=self.controller.thread, daemon=True)
        listen_thread.start()
        print("Listener thread started")
