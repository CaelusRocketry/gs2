# Simulation

> [!IMPORTANT] 
> The following information is in reference to the old flight software before commit [38dbe3914cbb9e5197c8515ba5a78227b85d0f54](https://github.com/CaelusRocketry/full-flight-software/commit/38dbe3914cbb9e5197c8515ba5a78227b85d0f54). If you have updated the flight software or cloned it after the aforementioned commit, then the flight software is already gs2-compatible and you do not need to modify it.

To test the Ground Station, you can run a simulation of the flight software by editing your environment to be `sim`. The simulation software can be found in the old flight software repository [here](https://github.com/CaelusRocketry/full-flight-software).

However, in its initial state, the simulation is incompatible with the Ground Station. Please review the instructions below to properly configure the flight software to run the simulation.

## Modifications

For the simulation to properly work, various modifications to the default configuration and code must be done.

### Configuration

The flight software's configuration is handled in [`full_config.json`](https://github.com/CaelusRocketry/full-flight-software/blob/b9db1e2cfec610a44dac1374aedaf7ec6088afc2/full_config.json). If you would not like to manually modify each property in the configuration please refer to the "modern" config provided [here](/docs/assets/sim_config.json).

#### Telemetry

- `GS_IP` and `GS_PORT` in the `telemetry` container should correspond to the `host` and `port` properties in the Ground Station's [configuration](/docs/CONFIG.md).

#### Sensors

- `Thermo-1` should be renamed to `TC-1` in the `thermocouple` container to conform with new naming conventions.
  - ```js
    // ...
    "sensors": {
      "list": {
        "thermocouple": {
          "TC-1": {
            // ...
    ``` 
- `PT-5`, `PT-P`, `PT-7`, and `PT-8` should be removed from the `pressure` list, leaving `PT-1` through `PT-4`.
  - ```js
    // ...
        "pressure": {
          "PT-1": {
            // ...
          }
          // PT-2, PT-3, ...
          "PT-4": {
            // ...
    ``` 
- A new container, `load_cell`, in `list` should be added and contain load cells `LC-1` to `LC-3`.
  - ```js
    // ...
      "list": {
        "load_cell": {
          "LC-1": {
            "kalman_args": {
                "process_variance": 0.01,
                "measurement_variance": 0.02,
                "kalman_value": 1000
              },
              "boundaries": {
                "waiting": {
                  "safe": [100, 500],
                  "warn": [50, 550]
                },
                "pressurization": {
                  "safe": [100, 500],
                  "warn": [50, 550]
                },
                "autosequence": {
                  "safe": [100, 500],
                  "warn": [50, 550]
                },
                "postburn": {
                  "safe": [100, 500],
                  "warn": [50, 550]
                }
              },
              "load_cell_pins": [0, 1, 2, 3],
              "bias": 1.0,
              "slope": 1.0
          }
          // LC-2, LC-3, ...
    ``` 

#### Valves

- **Note:** Although the Ground Station doesn't currently display valve data, it is still parsed and thus must be comply with the Ground Station.

- Add `ethanol_ground_vent` to the `solenoid` container with the label `NCSV-1`.
  - ```js
    // ...
    "valves": {
      "list": {
        "solenoid": {
          // ...
          "ethanol_mpv": {
            // ...
    ```
- Rename `ethanol_vent` in the same container to `nitrous_vent` with the label `NCSV-2`.
  - ```js
    // ...
          "nitrous_vent": {
            // ...
    ```
- Change `ethanol_pressurization` and `ethanol_mpv`'s labels to `NCSV-3` and `NCSV-9`, respectively.
  - ```js
    // ...
          "ethanol_pressurization": {
            "label": "NCSV-3",
            "pin": 6,
            "natural": "CLOSED"
          },
          // ...
          "ethanol_mpv": {
            "label": "NCSV-9",
            "pin": 12,
            "natural": "CLOSED"
          },
          // ...
    ```
- Add `nitrous_pressurization`, `ethanol_flight_vent`, `nitrous_flight_vent`, `ethanol_drain`, and `nitrous_drain` to the `solenoid` container with the labels `NCSV-4`, `NCSV-5`, `NCSV-6`, `NCSV-7`, and `NCSV-8`, respectively.
  - ```js
    // ...
          "nitrous_pressurization": {
            "label": "NCSV-4",
            "pin": 7,
            "natural": "CLOSED"
          },
          "ethanol_flight_vent": {
            "label": "NCSV-5",
            "pin": 8,
            "natural": "CLOSED"
          },
          "nitrous_flight_vent": {
              "label": "NCSV-6",
              "pin": 9,
              "natural": "CLOSED"
          },
          "ethanol_drain": {
              "label": "NCSV-7",
              "pin": 10,
              "natural": "OPEN"
          },
          "nitrous_drain": {
              "label": "NCSV-8",
              "pin": 11,
              "natural": "CLOSED"
          }
          // ...
    ```
- Add `nitrous_mpv` and `nitrous_isolation` with the labels `NCSV-A` and `NCSV-B`. These labels are in base-16 since the packet format sets valve locations to consist of only 1 character.
  - ```js
    // ...
          "nitrous_mpv": {
            "label": "NCSV-A",
            "pin": 13,
            "natural": "CLOSED"
          },
          "nitrous_isolation": {
            "label": "NCSV-B",
            "pin": 14,
            "natural": "CLOSED"
          }
          // ...
    ```

#### Task Configuration

- In the `task_config` container, remove `"stage"` from the `control_tasks` array and add `"telemetry"` to the `tasks` array. 
  - ```js
    // ...
    "task_config": {
      "tasks": ["sensor", "valve", "telemetry"],
      "control_tasks": ["sensor", "valve"]
    },
    // ...
    ```
### Modifying Header Types

In the old Ground Station, the packet format not only had more header types like `INF`, but also referred to existing header types like `SEN` and `VAL` as `DAT` and `VDT`. The old flight software hardcoded these header types, so you must find all occurrences of `DAT` and `VDT` and convert them to `SEN` and `VAL`.

#### ValveControl.cpp

```diff
# ...
-46 | global_flag.send_packet("VDT", mod_data);
+46 | global_flag.send_packet("VAL", mod_data);
``` 

#### SensorControl.cpp

```diff
# ...
-119 | global_flag.send_packet("DAT", data);
+119 | global_flag.send_packet("SEN", data);
```

### Load Cell Support

Load cells aren't supported by the old flight software by default, so you have to do some modifications to allow load cell reading.

#### SensorTask.cpp

```diff
# ...
 34 | #ifdef DESKTOP
 35 |   pressure_driver = new PseudoPressureDriver(pressure_pins);
 36 |   thermo_driver = new PseudoThermoDriver(thermo_pins);
+37 |   load_cell_driver = new PseudoLoadCellDriver(load_cell_pins);
# ...
 49 |   pressure_driver->read();
 50 |   thermo_driver->read();
+51 |   load_cell_driver->read();
# ...
+79 |   // Update load cell values
+80 |   for(unsigned int i = 0; i < load_cell_pins.size(); i++) {
+81 |     int pin = load_cell_pins[i][0];  
+82 |
+83 |     pair<string, string> sensor_info = pin_sensor_mappings[pin];
+84 |     string type = sensor_info.first;
+85 |     string loc = sensor_info.second;
+86 |     float value = load_cell_driver->getForceValue(pin);
+87 |     print(type + " " + loc + ": " + Util::to_string((double) value));
+88 |     global_registry.sensors[type][loc].measured_value = value;
+89 |   }
```

### Sensor & Valve Type Mappings

Like the Ground Station, the flight software keeps its own internal mappings of sensors and valves. Since we have altered the list of valves and sensors, we must modify these mappings accordingly.

#### SensorControl.hpp

```diff
# ...
 20 | unordered_map<string, string> sensor_type_map {
 21 |  {"thermocouple", "0"},
 22 |  {"pressure", "1"},
+23 |  {"load_cell", "2"}
 24 | };
# ...
 26 | unordered_map<string, string> sensor_location_map {
 27 |   {"PT-1", "1"},
 28 |   {"PT-2", "2"},
 29 |   {"PT-3", "3"},
 30 |   {"PT-4", "4"},
-31 |   {"PT-5", "5"},
-32 |   {"PT-P", "P"},
-33 |   {"PT-7", "7"},
-34 |   {"PT-8", "8"},
-35 |   {"Thermo-1", "9"},
+31 |   {"TC-1", "5"},
+32 |   {"LC-1", "6"},
+33 |   {"LC-2", "7"},
+34 |   {"LC-3", "8"},
 35 | };
```

#### ValveControl.hpp

```diff
# ...
 21 | std::unordered_map<std::string, std::string> valve_location_map {
-22 |  {"ethanol_pressurization", "1"},
-23 |  {"ethanol_vent", "2"},
-24 |  {"ethanol_mpv", "3"},
-26 |  {"nitrous_fill", "5"},
-27 |  {"nitrous_mpv", "6"},
+22 |  {"ethanol_ground_vent", "1"},
+23 |  {"nitrous_vent", "2"},
+24 |  {"ethanol_pressurization", "3"},
 25 |  {"nitrous_pressurization", "4"},
+26 |  {"ethanol_flight_vent", "5"},
+27 |  {"nitrous_flight_vent", "6"},
+28 |  {"ethanol_drain", "7"},
+29 |  {"nitrous_drain", "8"},
+30 |  {"ethanol_mpv", "9"},
+31 |  {"nitrous_mpv", "A"},
+32 |  {"nitrous_isolation", "B"}
 33 | };
```

#### TelemetryControl.hpp

```diff
# ...
 28 | unordered_map<string, string> sensor_type_inverse_map {
 29 |  {"0", "thermocouple"},
 30 |  {"1", "pressure"},
+31 |  {"2", "load_cell"}
 32 | };
# ...
 34 | unordered_map<string, string> sensor_location_inverse_map {
 35 |   {"1", "PT-1"},
 36 |   {"2", "PT-2"},
 37 |   {"3", "PT-3"},
 38 |   {"4", "PT-4"},
-39 |   {"5", "PT-5"},
-40 |   {"6", "PT-P"},
-41 |   {"7", "PT-7"},
-42 |   {"8", "PT-8"},
-43 |   {"9", "Thermo-1"},
+39 |   {"5", "TC-1"},
+40 |   {"6", "LC-1"},
+41 |   {"7", "LC-2"},
+42 |   {"8", "LC-3"},
 43 | };
# ...
 21 | std::unordered_map<std::string, std::string> valve_location_inverse_map {
-22 |  {"1", "ethanol_pressurization"},
-23 |  {"2", "ethanol_vent"},
-24 |  {"3", "ethanol_mpv"},
-26 |  {"5", "nitrous_fill"},
-27 |  {"6", "nitrous_mpv"},
+22 |  {"1", "ethanol_ground_vent"},
+23 |  {"2", "nitrous_vent"},
+24 |  {"3", "ethanol_pressurization"},
 25 |  {"4", "nitrous_pressurization"},
+26 |  {"5", "ethanol_flight_vent"},
+27 |  {"6", "nitrous_flight_vent"},
+28 |  {"7", "ethanol_drain"},
+29 |  {"8", "nitrous_drain"},
+30 |  {"9", "ethanol_mpv"},
+31 |  {"A", "nitrous_mpv"},
+32 |  {"B", "nitrous_isolation"}
 33 | };
```

## Running 

Information on how to run the flight software simulation can be found on its repository's [homepage](https://github.com/CaelusRocketry/full-flight-software#first-time-setup).