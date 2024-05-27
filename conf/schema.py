CONFIG_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "properties": {
        "environment": {"type": "string", "enum": ["simulation", "xbee"]},
        "telemetry": {
            "type": "object",
            "properties": {
                "sim": {
                    "type": "object",
                    "properties": {
                        "host": {"type": "string", "format": "ipv4"},
                        "port": {"type": "integer", "minimum": 1, "maximum": 65535},
                        "bufsize": {"type": "integer", "minimum": 2},
                        "delay": {"type": "number", "minimum": 0},
                    },
                    "required": ["host", "port", "bufsize", "delay"],
                },
                "xbee": {
                    "type": "object",
                    "properties": {"port": {"type": "string"}, "baudrate": {"type": "integer"}},
                    "required": ["port", "baudrate"],
                },
            },
            "required": ["sim", "xbee"],
        },
    },
    "required": ["environment", "telemetry"],
}
