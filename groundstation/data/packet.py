from django.conf import settings

class Packet:
    PACKET_START: str = '^'
    PACKET_DELIMITER: str = '|'
    PACKET_END: str = '$'

    DATA_DELIMITER: str = ','

    invalid = False

    def __init__(self, packed_pkt: str):
        # packed format: ^header|timestamp|data$
        if packed_pkt[0] != Packet.PACKET_START or packed_pkt[-1] != Packet.PACKET_END or len(packed_pkt.split(Packet.PACKET_DELIMITER)) != 3:
            self.invalid = True
            return

        self.unpack(packed_pkt)

    def unpack(self, packed_pkt: str):
        packet = packed_pkt[1:-1]
        tokens: list[str] = packet.split(self.PACKET_DELIMITER)
        print(tokens)
        self.header: str = tokens[0]
        self.data: str = tokens[2]
        # timestamp in this format to conform with old simulation software
        self.timestamp: float = int(tokens[1], base=16) / 1000.0

    def parse(self):
        header = self.header.upper()
        header_name = self.get_header_name()

        response: dict = {
            'header': header_name,
            'timestamp': self.timestamp,
            'payload': {}
        }

        if header == 'SEN':
            self.parse_sensors(response)
        elif header == 'VAL':
            self.parse_valves(response)

        return response

    def parse_sensors(self, response: dict):
        sensors: list[str] = self.data.split(self.DATA_DELIMITER)

        for sensor in sensors:
            sensor_type, sensor_location, sensor_callibration = self.get_sensor_data(sensor)
            value = int(sensor[2:], 16)
            # print(sensor_callibration)
            if sensor_type not in response['payload']:
                response['payload'][sensor_type] = {}

            response['payload'][sensor_type][sensor_location] = value + sensor_callibration
            # print(response['payload'][sensor_type][sensor_location], value)

    def parse_valves(self, response: dict):
        valves: list[str] = self.data.split(self.DATA_DELIMITER)

        for valve in valves:
            valve_type, valve_location = self.get_valve_data(valve)
            state = int(valve[2])

            if valve_type not in response['payload']:
                response['payload'][valve_type] = {}

            response['payload'][valve_type][valve_location] = state

    def get_header_name(self):
        name_mapping: dict = {
            'SEN': "sensor_data",
            'VAL': "valve_data",
            # conform with old simulation software
            'INF': "info"
        }

        return name_mapping[self.header]

    def get_sensor_data(self, sensor: str):
        type_mapping: dict = {
            '0': 'thermocouple', 
            '1': 'pressure', 
            '2': 'load'
        }

        # subject to change
        location_mapping: dict = {
            '1': 'PT-1', 
            '2': 'PT-2', 
            '3': 'PT-3', 
            '4': 'PT-4', 
            '5': 'TC-1',
            '6': 'LC-1',
            '7': 'LC-2',
            '8': 'LC-3'
        }
        callibration = 0
        if location_mapping[sensor[1]] in settings.SENSOR_CALIBRATION_MAPPING:
            callibration = settings.SENSOR_CALIBRATION_MAPPING[location_mapping[sensor[1]]]
        return type_mapping[sensor[0]], location_mapping[sensor[1]], callibration

    def get_valve_data(self, valve: str):
        # in case there will be more than 1 type
        type_mapping: dict = {
            "0": "solenoid"
        }

        # subject to change
        location_mapping: dict = {
            "1": "SV-1",  # ethanol_ground_vent
            "2": "SV-2",  # nitrous_vent
            "3": "SV-3",  # ethanol_pressurization
            "4": "SV-4",  # nitrous_pressurization
            "5": "SV-5",  # ethanol_flight_vent
            "6": "SV-6",  # nitrous_flight_vent
            "7": "SV-7",  # ethanol_drain
            "8": "SV-8",  # nitrous_drain
            "9": "SV-9",  # ethanol_mpv
            "A": "SV-10",  # nitrous_mpv
            "B": "SV-11",  # nitrous_isolation
        }

        return type_mapping[valve[0]], location_mapping[valve[1]]

    def __str__(self):
        return f"{self.PACKET_START}{self.header}{self.PACKET_DELIMITER}{self.timestamp}{self.PACKET_DELIMITER}{self.data}{self.PACKET_END}"
