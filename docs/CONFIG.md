# Configuration

All configuration that affects the Ground Station is located at `groundstation/config.json`. 

## Structure

The configuration is a JSON file structured as
```js
{
    "environment": "xbee" | "sim" | "bt",
    "telemetry": {
        "sim": {
            "host": IPv4,
            "port": number,
            "bufsize": number,
            "delay": float,
            "timeout": number,
            "max_retries": number,
            "store": "parsed" | "packed"
        },
        "xbee": {
            "port": `COM${number}` | `/dev/ttyUSB${number}`,
            "baudrate": number,
            "delay": float,
            "timeout": number,
            "max_retries": number,
            "store": "parsed" | "packed"
        },
        "bt":  {
            "name": string,
            "port": number,
            "bufsize": number,
            "delay": float,
            "timeout": number,
            "max_retries": number,
            "store": "parsed" | "packed"
        }
    }
}
```

### Environment

This property determines whether the Ground Station will interface with a flight software simulation, an XBee socket, or a Bluetooth socket. Use `"sim"` for the simulation environment, `"xbee"` for the XBee environment, and `"bt"` for the Bluetooth environment.

### Telemetry

This is a container that supports additional configuration for both environments.

### Host

This is a web address for the socket which is almost always `127.0.0.1` or `localhost`.
- **Note:** This option does not exist in XBee or Bluetooth configuration.

### Name

This is the name of the Bluetooth Serial created in the flight software. A name like `SensorPCB` will most likely be used. 
- **Note:** This only exists on the Bluetooth configuration.

### Port 

For the simulation environment, this will the port for the socket. You may connect to any open port between 0 to 65535.

For the XBee environment, this will be the port that the XBee is attached to. 

##### Windows
On Windows, this port will be in the form `COM<number>`, such as `COM5`.  

##### Linux
On Linux, this port will be in the form `/dev/ttyUSB<number>`, such as `/dev/ttyUSB0`. To gain access to the USB device, run `sudo adduser $USER dialout` and logout and login again. If this doesn't work, try running `sudo chmod 666 /dev/ttyUSB<number>.`

### Bufsize / Baudrate

For the simulation & bluetooth environment, this option is called **`bufsize`** and it determines the size of the buffer that Python will send to the socket to input bytes in. In other words, this determines how much data can be received. 

For the XBee environment, this option is called **`baudrate`** and it is a measure of the speed at which the data is transmitted from the XBee device. It is measured in bps (bits per second) and is usually `9600`.

### Delay

This is the number of seconds that the socket loop will wait before each interation.

### Timeout

This is the number of seconds that the Ground Station will wait until it determines that the socket is disconnected.

### Max Retries

This specifies the number of connection attempts the Ground Station will make to the socket before giving up.

### Store

This is determines whether the Ground Station will store the incoming packets as-is or as parsed JSON data.