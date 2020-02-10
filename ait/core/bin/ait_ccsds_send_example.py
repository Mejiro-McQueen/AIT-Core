#!/usr/bin/env python

import socket
import struct
import time
from ait.core import log, tlm

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
hs_packet = struct.Struct('>BBBBBBBB')
data = bytearray(b'\x02\xE7\x40\x00\x00\x01\x00\x01')

'''
version:                    000
type:                       0
secondary header flag:      0
apid:                       01011100111
sequence flag:              01
sequence count:             00000000000000
packet length:              0000000000000001
data:                       00000000 00000001
'''

buf = hs_packet.pack(*data)

host = 'localhost'
port = 3076

while True:
    s.sendto(buf, (host, port))
    log.info('Sent telemetry (%d bytes) to %s:%d' 
                % (hs_packet.size, host, port))
    time.sleep(1)
