# Packet

Data transmitted by the flight software to the ground software is called a "packet".

## Structure

![Packet Structure](/docs/assets/packet.png)

## Constants

As specified in the structure, the format constants are as following:
```yaml
Packet Start: `^`  
Packet End: `$`  
Packet Delimiter: `|`  
Data Delimiter: `,`
```

## Timestamp

The timestamp is a base-16 encoded number that represents the time elapsed in milliseconds. The Ground Station represents the timestamp as the time elapsed in **seconds** internally.

## Types

### SEN

The `SEN` packet is used to send sensor-related data. The data is in the format of `<sensor_type><sensor_location><...value>`. The sensor type is a number between 0 and 2 and maps to thermocouple, pressure, or load. The sensor location is a number between 1 and 8 and maps to PT-1, ..., PT-4, TC-1, LC-1, ..., LC-3. The sensor value consists of the rest of the data which is a number in base 16.

### VAL

The `VAL` packet is used to send valve-related data. The data is in the format of `<valve_type><valve_location><state>`. The valve type is always 0, which maps to solenoid. The valve location is a number in base 16 between 1 and B and maps to SV-1, ..., SV-11. The valve state is a number that represents the current state of the valve.
- **Note:** Valve data is currently not read, so this packet will not be encountered.

### END

The `END` packet is a special type of packet: it has no data and is in the format `^END|<timestamp>$`. This packet tells the Ground Station to terminate the current test and mark its status in the database as `Completed`. This packet may not be sent at all, so you might not encounter it.

## Parsed Packet 

Once the Ground Station parses a packet, it sends the structure to the frontend. For a `SEN` packet, this structure looks like:
```js
{
    header: "SEN",
    payload: {
        load: {
            "LC-1": number,
            // ...
            "LC-3": number
        },
        pressure: {
            "PT-1": number,
            // ...
            "PT-4": number
        },
        thermocouple: {
            "TC-1": number
        }
    },
    timestamp: number
}
```

For a `VAL` packet, this structure looks like:
```js
{
    header: "VAL",
    payload: {
        solenoid: {
            "SV-1": number,
            // ...
            "SV-11": number
        }
    },
    timestamp: number
}
```