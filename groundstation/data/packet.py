from groundstation import settings

class Packet:
    PACKET_START: str = "^"
    PACKET_DELIMITER: str = "|"
    PACKET_END: str = "$"

    STAGE_DELIMITER: str = "-"
    DATA_DELIMITER: str = ","
    
    def __init__(self, raw="", header="", data="", timestamp=None):
        if raw:
            self.unpack(raw)
        else:
            # TODO: handle empty packets
            self.header: str = header
            self.data: str = data
            self.timestamp: float = timestamp

    def unpack(self, packet):
        packet = packet[1:-1]
        tokens: list[str] = packet.split(self.PACKET_DELIMITER)
        self.header: str = tokens[0]
        self.data: str = tokens[2]
        self.timestamp: float = int(tokens[1], base=16) / 1000.0

    def parse(self):
        header = self.header.upper()
        header_name = self.get_header_name()
        header_type = self.get_header_type()

        response: dict = {
            "header": header_name,
            "timestamp": self.timestamp,
            "payload": {
                "type": header_type
            }
        }

        if header == "DAT":
            self.parse_sensors(response)
        elif header == "VDT":
            self.parse_valves(response)
        elif header == "SGP":
            stage_data: list[str] = self.data.split(self.STAGE_DELIMITER)
            if stage_data[1] == "1":
                response["payload"]["message"] = f"progressed_{self.get_stage_name(stage_data[0], 0)}"
        elif header == "SGD":
            response["payload"]["stage"] = self.get_stage_name(self.data, 0)
            response["payload"]["status"] = int(self.data[1:])
        elif header == "SPQ":
            response["payload"]["message"] = f"permission_to_progress_{self.get_stage_name(self.data, 1)}"
        elif header == "HRT":
            response["payload"]["message"] = "ok"
        elif header == "SAB":
            response["payload"]["mode"] = "soft_abort"
        elif header == "UAB":
            response["payload"]["mode"] = "normal"
        else:
            response["payload"]["message"] = self.data

        return response

    def parse_sensors(self, response: dict):
        sensors: list[str] = self.data.split(self.DATA_DELIMITER)
            
        for sensor in sensors:
            sensor_type, sensor_location = self.get_sensor_data(sensor)
            value = int(sensor[2:], 16)

            if not sensor_type in response["payload"]:
                response["payload"][sensor_type] = {}
            if not sensor_location in response["payload"]:
                response["payload"][sensor_type][sensor_location] = {}

            if sensor_type == "pressure":
                # slope and bias values should be calibrated
                slope = float(settings.CONFIG["sensors"]["pressure"][sensor_location]["slope"])
                bias = float(settings.CONFIG["sensors"]["pressure"][sensor_location]["bias"])
                value = slope * value + bias # adjust to y=mx+b
            
            response["payload"][sensor_type][sensor_location]["value"] = value

    def parse_valves(self, response: dict):
        valves: list[str] = self.data.split(self.DATA_DELIMITER)

        for valve in valves:
            valve_type, valve_location = self.get_valve_data(valve)
            state = int(valve[2])

            if not valve_type in response["payload"]:
                response["payload"][valve_type] = {}
            
            response["payload"][valve_type][valve_location] = state

    def get_header_name(self):
        name_mapping: dict = {
            "HRT": "heartbeat",
            "SAB": "mode",
            "UAB": "mode",
            "AAB": "response",
            "SAC": "response",
            "SDT": "response",
            "DAT": "sensor_data",
            "VST": "response",
            "VDT": "valve_data",
            "SGP": "stage_progress",
            "SPQ": "response",
            "SGD": "stage",
            "INF": "response"
        }

        return name_mapping[self.header]

    def get_header_type(self):
        type_mapping: dict = {
            "HRT": "heartbeat",
            "SAB": "mode",
            "UAB": "mode",
            "AAB": "response",
            "SAC": "valve_actuation",
            "SDT": "sensor_data",
            "DAT": "sensor_data",
            "VST": "valve_data_request",
            "VDT": "valve_data",
            "SGP": "stage_progression",
            "SPQ": "stage_progression_request",
            "SGD": "stage_data",
            "INF": "info"
        }

        return type_mapping[self.header]

    def get_sensor_data(self, sensor: str):
        type_mapping: dict = {
            "0": "thermocouple", 
            "1": "pressure", 
            "2": "load"
        }

        location_mapping: dict = {
            "1": "PT-1", 
            "2": "PT-2", 
            "3": "PT-3", 
            "4": "PT-4", 
            "5": "PT-5", 
            "P": "PT-6", 
            "7": "PT-7", 
            "8": "PT-8", 
            "9": "TC-1",
            "A": "TC-2",
            "B": "TC-3",
            "C": "TC-4",
            "D": "LC-1",
            "E": "LC-2",
            "F": "LC-3",
        }

        return (type_mapping[sensor[0]], location_mapping[sensor[1]])

    def get_valve_data(self, valve: str):
        # in case there will be more than 1 type
        type_mapping: dict = {
            "0": "solenoid"
        }
        
        location_mapping: dict = {
            "1": "ethanol_pressurization",
            "2": "ethanol_vent",
            "3": "ethanol_mpv",
            "4": "nitrous_pressurization",
            "5": "nitrous_fill",
            "6": "nitrous_mpv"
        }

        return (type_mapping[valve[0]], location_mapping[valve[1]])

    def get_stage_name(self, stage: str, index: int):
        name_mapping = {
            "1": "waiting",
            "2": "pressurization",
            "3": "autosequence",
            "4": "postburn",
        }

        return name_mapping[stage[index]]

    def __str__(self):
        return f"{self.PACKET_START}{self.header}{self.PACKET_DELIMITER}{self.timestamp}{self.PACKET_DELIMITER}{self.data}{self.PACKET_END}"

    def __eq__(self, other):
        self.timestamp == other.timestamp

    def __lt__(self, other):
        # sort outgoing heapq by the order in which it arrived
        self.timestamp < other.timestamp