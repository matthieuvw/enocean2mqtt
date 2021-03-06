# Global configuration

```yaml
enocean:

  port: /dev/ttyAMA0
  base_id: [0xFF, 0xFF, 0xFF, 0xFF]  # Your EnOcean base ID here (optional)

mqtt:

  host: localhost
  port: 1883
  client_id: enocean2mqtt
  topic_prefix: enocean2mqtt

devices:

  - name: friendly_name # Friendly name for topic
    address: [0xFF, 0xFF, 0xFF, 0xFF] # EnOcean device ID
    eep: [0xd2, 0x01, 0x01] # EnOcean device EEP
    data: ["OV"] # EnOcean EEP data to publish
    group_by: ["IO"] # Group data to publish on topic
    json: true # Publish in JSON format
    last_seen: true # Publish packet received date
    command: true # Accept command to this device
```

# Devices configuration

## Default behaviour

Publish once per data contained in radio packet : `<mqtt.topic_prefix>/<device.name>/<data_shortcut> <value>`

```yaml
devices:
  - name: my_2ch_switch
    address: [0xFF, 0xFF, 0xFF, 0xFF]
    eep: [0xd2, 0x01, 0x01]
```
```
# published :
enocean2mqtt/my_2ch_switch/OV 100
enocean2mqtt/my_2ch_switch/PF 0
enocean2mqtt/my_2ch_switch/PFD 0
enocean2mqtt/my_2ch_switch/CMD 4
enocean2mqtt/my_2ch_switch/OC 0
enocean2mqtt/my_2ch_switch/EL 3
enocean2mqtt/my_2ch_switch/LC 1
enocean2mqtt/my_2ch_switch/IO 0
```

## `device.json`

Publish once per received radio packet : `<mqtt.topic_prefix>/<device.name> {<data_shortcut>: <value>}`

```yaml
devices:
  - name: my_2ch_switch
    address: [0xFF, 0xFF, 0xFF, 0xFF]
    eep: [0xd2, 0x01, 0x01]
    json: true
```
```
# published :
enocean2mqtt/my_2ch_switch {"PF": 0, "PFD": 0, "CMD": 4, "OC": 0, "EL": 3, "IO": 0, "LC": 1, "OV": 100}
```

## `device.data`

Filter published data.

```yaml
devices:
  - name: my_2ch_switch
    address: [0xFF, 0xFF, 0xFF, 0xFF]
    eep: [0xd2, 0x01, 0x01]
    data: ["OV", "LC"]
```
```
# Default
enocean2mqtt/my_2ch_switch/OV 100
enocean2mqtt/my_2ch_switch/LC 1

# JSON format
enocean2mqtt/my_2ch_switch {"LC": 1, "OV": 100}
```

## `device.group_by`

Group publishing by data value (useful for distinguishing between channels on relay).
> Each data in `group_by` append `/<data_shortcut>/<value>` to topic
> If you use multiple values in `group_by`, order is respected in topic.

```yaml
devices:
  - name: my_2ch_switch
    address: [0xFF, 0xFF, 0xFF, 0xFF]
    eep: [0xd2, 0x01, 0x01]
    data: ["OV"]
    group_by: ["IO"]
```
```
# Default
enocean2mqtt/my_2ch_switch/IO/0/OV 100 # first channel
enocean2mqtt/my_2ch_switch/IO/1/OV 100 # second channel

# JSON format
enocean2mqtt/my_2ch_switch/IO/0 {"OV": 100} # first channel
enocean2mqtt/my_2ch_switch/IO/1 {"OV": 100} # second channel
```

## `device.last_seen`

Publish radio packet received date.

```yaml
devices:
  - name: my_2ch_switch
    address: [0xFF, 0xFF, 0xFF, 0xFF]
    eep: [0xd2, 0x01, 0x01]
    data: ["OV"]
    group_by: ["IO"]
    last_seen: true
```
```
# Default
enocean2mqtt/my_2ch_switch/IO/0/OV 100 # first channel
enocean2mqtt/my_2ch_switch/IO/0/last_seen 2021-03-05T23:01:11.316657 # first channel
enocean2mqtt/my_2ch_switch/IO/1/OV 100 # second channel
enocean2mqtt/my_2ch_switch/IO/1/last_seen 2021-03-05T23:18:48.047640 # second channel

# JSON format
enocean2mqtt/my_2ch_switch/IO/0 {"OV": 100, "last_seen": 2021-03-05T23:01:11.316657} # first channel
enocean2mqtt/my_2ch_switch/IO/1 {"OV": 100, "last_seen": 2021-03-05T23:18:48.047640} # second channel
```

## `device.command`

Allows to transmit radio packet to device.  
enocean2mqtt subscribe to `<mqtt.topic_prefix>/<device.name>/command` to receive commands and build packet data from message.

```bash
# Turn on channel 0 of my_2ch_switch
mosquitto_pub -h localhost -p 1883 -t enocean2mqtt/my_2ch_switch/command -m '{"CMD":1,"IO":0,"OV":100}'
```
