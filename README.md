# enocean2mqtt

* publish EnOcean received packets to MQTT
* Send commands to EnOcean equipments via MQTT

It is based on [Python EnOcean](https://github.com/kipe/enocean) and [Eclipse Paho™ MQTT Python Client](https://github.com/eclipse/paho.mqtt.python).

## Install

```
pip install encoean2mqtt --user
```

For Linux systems pip install package by default in `~/.local/lib` (check with `python -m site --user-site`)
pip installation added python lib to `~/.local/lib` and command `~/.local/bin/enocean2mqtt`
(add `export PATH="$HOME/bin:$PATH"` to file `~/.bashrc`)

## Configure

Get inspired by [enocean2mqtt-sample.yaml](https://github.com/matthieuvw/enocean2mqtt/blob/main/resources/enocean2mqtt-sample.yaml) and/or read [configuration documentation on GitHub](https://github.com/matthieuvw/enocean2mqtt/blob/main/doc/configuration.md)

## Run manually

```
# Minimal
~/.local/bin/enocean2mqtt --config /your/path/enocean2mqtt.yaml

# All args
~/.local/bin/enocean2mqtt --config /your/path/enocean2mqtt.yaml --verbose --log-file /your/path/enocean2mqtt.log
```

Args:
| Short | Long       | Required | Description                      |
| :---- | :--------- | :------: | :------------------------------- |
| -c    | --config   | yes      | yaml config file                 |
| -v    | --verbose  | no       | Set logging level to DEBUG       |
| N/A   | --log-file | no       | Add daily rotating log file path |

## Run as a systemd service

> Sample made for Raspbian 10 and `pi` user

* copy file [enocean2mqtt.service](https://github.com/matthieuvw/enocean2mqtt/blob/main/resources/enocean2mqtt.service) to `/etc/systemd/system/enocean2mqtt.service`
* customize with your user and configuration file path
* `sudo chown root:root /etc/systemd/system/enocean2mqtt.service`
* `sudo chmod 644 /etc/systemd/system/enocean2mqtt.service`
* `sudo systemctl daemon-reload`
* `sudo systemctl enable enocean2mqtt`
* `sudo systemctl start enocean2mqtt`

Check status : `sudo systemctl status enocean2mqtt`  
See logs : `journalctl -f -u enocean2mqtt`  
