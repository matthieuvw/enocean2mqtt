# -*- encoding: utf-8 -*-

import enocean2mqtt.conf as conf

CONGIG_SCHEMA = {
    "$schema": "http://json-schema.org/schema#",
    "title": "Schema de configuration enocean2mqtt",
    "type": "object",
    "required": [conf.ENOCEAN, conf.MQTT, conf.DEVICES],
    "properties": {
        conf.ENOCEAN: {
            "type": "object",
            "required": [conf.ENOCEAN_PORT],
            "properties": {
                conf.ENOCEAN_PORT: {"type": "string", "minLength": 1},
                conf.ENOCEAN_BASE_ID: {
                    "type": "array",
                    "minItems": 4,
                    "maxItems": 4,
                    "items": {"type": "number", "minimum": 0, "maximum": 255}
                }
            }
        },
        conf.MQTT : {
            "type": "object",
            "required": [conf.MQTT_HOST, conf.MQTT_PORT, conf.MQTT_TOPIC_PREFIX],
            "properties": {
                conf.MQTT_HOST: {"type": "string"},
                conf.MQTT_PORT: {"type": "number"},
                conf.MQTT_TOPIC_PREFIX: {"type:": "string"}
            }
        },
        conf.DEVICES: {
            "type": "array",
            "items": {
                "type": "object",
                "required": [conf.DEVICE_NAME, conf.DEVICE_ADDRESS, conf.DEVICE_EEP],
                "properties": {
                    conf.DEVICE_NAME: { "type": "string", "minLength": 1},
                    conf.DEVICE_ADDRESS: {
                        "type": "array",
                        "minItems": 4,
                        "maxItems": 4,
                        "items": {"type": "number", "minimum": 0, "maximum": 255}
                    },
                    conf.DEVICE_EEP: {
                        "type": "array",
                        "minItems": 3,
                        "maxItems": 3,
                        "items": { "type": "number", "minimum": 0, "maximum": 255}
                    },
                    conf.DEVICE_GROUP_BY: {
                        "type": "array",
                        "items": {"type": "string", "minLength": 1}
                    },
                    conf.DEVICE_DATA: {
                        "type": "array",
                        "items": {"type": "string", "minLength": 1}
                    },
                    conf.DEVICE_COMMAND: { "type": "boolean"},
                    conf.DEVICE_RETAIN: { "type": "boolean"},
                    conf.DEVICE_JSON: { "type": "boolean"},
                    conf.DEVICE_LAST_SEEN: { "type": "boolean"}
                }
            }
        }
    }
}
