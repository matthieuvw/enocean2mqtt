# -*- encoding: utf-8 -*-

import logging
import json
import numbers
import re
import queue
from types import SimpleNamespace
from jsonschema import validate
from enocean.communicators import SerialCommunicator
from enocean.protocol.packet import Packet, RadioPacket, UTETeachInPacket
from enocean.protocol.constants import PACKET, RETURN_CODE
import enocean.utils
import paho.mqtt.client as mqtt
import enocean2mqtt.conf as conf
import enocean2mqtt.schema as schema
import enocean2mqtt.strings as strings
import enocean2mqtt.utils as utils
from enocean2mqtt.device import Device

TRUE_VALUES = ['True', 'true', 'yes', '1', 'on', 'enable']
FALSE_VALUES = ['False', 'false', 'no', '0', 'off', 'disable']
DEVICE_COMMAND_TOPIC_SUFFIX = '/command'
CONF_TOPIC = '/conf'
TEACHIN_GETTER_CONF_TOPIC = CONF_TOPIC + '/teach_in'
TEACHIN_SETTER_CONF_TOPIC = TEACHIN_GETTER_CONF_TOPIC + '/set'
MQTT_BOOLEAN_PAYLOADS = { True: '1', False: '0'}

class Communicator:

    logger = logging.getLogger('enocean2mqtt.communicator')

    def __init__(self, config):

        validate(config, schema.CONGIG_SCHEMA)
        self.logger.debug('Configuration validated')

        self._enocean_config = config[conf.ENOCEAN]
        self._mqtt_config = config[conf.MQTT]

        # Devices
        self._devices_by_address = {}
        self._devices_by_name = {}
        for device_config in config[conf.DEVICES]:
            new_device = Device(device_config)
            self._devices_by_address[enocean.utils.to_hex_string(new_device.address)] = new_device
            self._devices_by_name[new_device.name] = new_device
            self.logger.debug(f'Device {new_device} loaded')

        # EnOcean
        self._communicator = SerialCommunicator(port=self._enocean_config[conf.ENOCEAN_PORT])
        base_id = self._enocean_config.get(conf.ENOCEAN_BASE_ID, None)
        if base_id:
            self._communicator.base_id = base_id
        self.logger.info(f'EnOcean serial communicator ready on {self._enocean_config[conf.ENOCEAN_PORT]}')

        # MQTT
        self._mqtt = mqtt.Client(client_id=self._mqtt_config[conf.MQTT_CLIENT_ID])
        self._mqtt.on_connect = self._mqtt_on_connect
        self._mqtt.on_disconnect = self._mqtt_on_disconnect
        self._mqtt.on_message = self._mqtt_on_message
        self._mqtt.enable_logger()
        self._mqtt.connect_async(
            self._mqtt_config[conf.MQTT_HOST],
            port=self._mqtt_config[conf.MQTT_PORT],
            keepalive=60)
        self.logger.info(f'MQTT broker ready on {self._mqtt_config[conf.MQTT_HOST]}:{self._mqtt_config[conf.MQTT_PORT]}')

    def start(self):

        self._communicator.start()
        self.logger.debug('EnOcean serial communicator started')

        port_base_id = enocean.utils.to_hex_string(self._communicator.base_id)
        if self._communicator.base_id is None:
            raise Exception(f'Cannot get base ID from device {self._enocean_config[conf.ENOCEAN_PORT]}')
        else:
            self.logger.info(f'EnOcean module base id is {port_base_id}.')

        self._mqtt.loop_start()
        self.logger.debug('MQTT client started')

        while self._communicator.is_alive():

            try:
                packet = self._communicator.receive.get(block=True, timeout=1)
                self._consume_enocean_packet(packet)
            except queue.Empty:
                continue
            except KeyboardInterrupt:
                self.logger.debug('KeyboardInterrupt')
                break
            except Exception:
                traceback.print_exc(file=sys.stdout)
                break

        if self._communicator.is_alive():
            self._communicator.stop()

    def _consume_enocean_packet(self, packet):

        if not isinstance(packet, Packet):
            self.logger.error('Object to handle must be an instance of Packet')
            return False

        if packet.packet_type == PACKET.RADIO:

            device = self._devices_by_address.get(enocean.utils.to_hex_string(packet.sender), None)

            if device is None:
                self.logger.warning(f'Packet skipped : no device found in configuration for address {packet.sender}')
                return True

            if isinstance(packet, UTETeachInPacket):
                self.logger.info(f'Receive teach-in packet from {device}')
                return True
            else:
                group_by_data, data = device.parse(packet)
                if data:
                    topic_suffix = ''.join([ f'/{k}/{v}' for k, v in group_by_data.items()])
                    topic = f'{self._mqtt_config[conf.MQTT_TOPIC_PREFIX]}/{device.name}{topic_suffix}'
                    if device.json:
                        self._mqtt.publish(topic, json.dumps(data), retain=device.retain)
                    else:
                        for k,v in data.items():
                            self._mqtt.publish(f'{topic}/{k}', v, retain=device.retain)

        elif packet.packet_type == PACKET.RESPONSE:
            self.logger.info(f'Response packet: {RETURN_CODE(packet.data[0]).name}')
        else:
            self.logger.warning(f'Packet of type \'{packet.packet_type}\' not handle')


    def _mqtt_on_connect(self, mqtt_client, userdata, flags, rc):

        if rc == 0:

            self.logger.info("Succesfully connected to MQTT broker.")

            self._mqtt.subscribe(f'{self._mqtt_config[conf.MQTT_TOPIC_PREFIX]}{TEACHIN_SETTER_CONF_TOPIC}/#')

            for device in self._devices_by_address.values():
                if device.command:
                    self._mqtt.subscribe(f'{self._mqtt_config[conf.MQTT_TOPIC_PREFIX]}/{device.name}{DEVICE_COMMAND_TOPIC_SUFFIX}/#')

            self._publish_conf()

        else:
            self.logger.error(f'Error connecting to MQTT broker: {strings.MQTT_CONNECTION_RETURN_CODES[rc]}')


    def _mqtt_on_disconnect(self, mqtt_client, userdata, rc):

        if rc == 0:
            self.logger.warning('Successfully disconnected from MQTT broker')
        else:
            self.logger.warning(f'Unexpectedly disconnected from MQTT broker: {strings.MQTT_CONNECTION_RETURN_CODES[rc]}')

    def _mqtt_on_message(self, mqtt_client, userdata, msg):

        if msg.topic.endswith(DEVICE_COMMAND_TOPIC_SUFFIX):
            self._consume_mqtt_message_command(mqtt_client, userdata, msg)
        elif msg.topic.startswith(self._mqtt_config[conf.MQTT_TOPIC_PREFIX]+CONF_TOPIC):
            self._consume_mqtt_message_conf(mqtt_client, userdata, msg)

    def _consume_mqtt_message_conf(self, mqtt_client, userdata, msg):

        if msg.topic.endswith(TEACHIN_SETTER_CONF_TOPIC):

            new_teach_in_raw_value = str(msg.payload, 'utf-8')

            new_teach_in_value = None
            if new_teach_in_raw_value in TRUE_VALUES:
                new_teach_in_value = True
            elif new_teach_in_raw_value in FALSE_VALUES:
                new_teach_in_value = False

            if new_teach_in_value is not None:
                self.logger.info(f'Configuration change : teach_in => {new_teach_in_value} (payload={msg.payload})')
                self._communicator.teach_in = new_teach_in_value
                self._mqtt.publish(
                    f'{self._mqtt_config[conf.MQTT_TOPIC_PREFIX]}{TEACHIN_GETTER_CONF_TOPIC}',
                    MQTT_BOOLEAN_PAYLOADS[self._communicator.teach_in],
                    retain=True)
            else:
                logger.error(f'Invalid value for teach-in : {new_teach_in_raw_value}')

    def _consume_mqtt_message_command(self, mqtt_client, userdata, msg):

        m = re.search(f'(?<={self._mqtt_config[conf.MQTT_TOPIC_PREFIX]}/)[^/]+(?={DEVICE_COMMAND_TOPIC_SUFFIX})', msg.topic)

        if m is None:
            self.logger.error(f'Cannot find device name in topic {msg.topic}')
        else:
            device = self._devices_by_name.get(m.group(0), None)
            if device is not None:

                payload_args = json.loads(msg.payload)

                command_args = {
                    'rorg': device.eep[0],
                    'rorg_func': device.eep[1],
                    'rorg_type': device.eep[2],
                    'sender': self._communicator.base_id,
                    'destination': device.address
                }

                command_args.update(payload_args)

                packet_to_send = None
                try:
                    packet_to_send = RadioPacket.create(**command_args)
                except:
                    self.logger.error(f'Cannot create radio packet to send for {command_args}')

                if packet_to_send:
                    try:
                        self._communicator.send(packet_to_send)
                    except:
                        self.logger.error(f'Cannot send radio packet')

            else:
                self.logger.error(f'Cannot find device named {dest_device_name}')

    def _publish_conf(self):

        self._mqtt.publish(
            f'{self._mqtt_config[conf.MQTT_TOPIC_PREFIX]}{TEACHIN_GETTER_CONF_TOPIC}',
            MQTT_BOOLEAN_PAYLOADS[self._communicator.teach_in],
            retain=True)
