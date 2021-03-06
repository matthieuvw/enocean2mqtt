# -*- encoding: utf-8 -*-

import enocean2mqtt.conf as conf
import enocean2mqtt.utils as utils
from enocean.protocol.packet import RadioPacket
import collections
import logging
from datetime import datetime
from enocean.protocol.constants import PARSE_RESULT

class Device:

    logger = logging.getLogger('enocean2mqtt.Device')

    _name = None
    _address = None
    _eep = None
    _group_by = []
    _data = []
    _command = False
    _retain = True
    _json = False
    _last_seen = False

    def __init__(self, device_config):
        self._name = device_config.get(conf.DEVICE_NAME, None)
        self._address = device_config.get(conf.DEVICE_ADDRESS, None)
        self._eep = device_config.get(conf.DEVICE_EEP)
        self._group_by = device_config.get(conf.DEVICE_GROUP_BY, [])
        self._data = device_config.get(conf.DEVICE_DATA, [])
        self._command = device_config.get(conf.DEVICE_COMMAND, False)
        self._retain = device_config.get(conf.DEVICE_RETAIN, True)
        self._json = device_config.get(conf.DEVICE_JSON, False)
        self._last_seen = device_config.get(conf.DEVICE_LAST_SEEN, False)

    @property
    def name(self):
        return self._name

    @property
    def address(self):
        return self._address

    @property
    def eep(self):
        return self._eep

    @property
    def command(self):
        return self._command

    @property
    def retain(self):
        return self._retain

    @property
    def json(self):
        return self._json

    def __str__(self):
        return f'{self.name} {utils.to_hex_string(self.address)}'

    def parse(self, packet):

        if not isinstance(packet, RadioPacket):
            self.logger.error('packet must be an instance of RadioPacket')
            return None, None

        shortcuts = packet.parse_eep(self._eep[1], self._eep[2])
        
        if not shortcuts:
            return None, None

        group_by_data = collections.OrderedDict()
        for group_by_shortcut in self._group_by:
            if group_by_shortcut in shortcuts:
                group_by_data[group_by_shortcut] = utils.get_data_value_by_shortcut(packet, group_by_shortcut)
                shortcuts.remove(group_by_shortcut)
            else:
                logging.error(f'Packet data does not contain {group_by_shortcut} group shortcut')
                return None, None

        if self._data:
            data_shortcuts = self._data
        else:
            data_shortcuts = shortcuts

        data = {}
        for shortcut in data_shortcuts:
            data[shortcut] = utils.get_data_value_by_shortcut(packet, shortcut)

        if self._last_seen:
            data[conf.DEVICE_LAST_SEEN] = packet.received.isoformat()

        return group_by_data, data
