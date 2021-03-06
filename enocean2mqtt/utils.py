# -*- encoding: utf-8 -*-

import numbers

def get_data_value_by_shortcut(packet, shortcut):
    kv = packet.parsed[shortcut]
    return kv['value'] if isinstance(kv['value'], numbers.Number) else kv['raw_value']

def to_hex_string(int_array):
    array_content = ', '.join('0x{:02x}'.format(i) for i in int_array)
    return f'[{array_content}]'
