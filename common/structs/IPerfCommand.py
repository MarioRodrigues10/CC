from enum import Enum
import struct
from typing import Self

from common.structs.Command import Command

class TransportProtocol(Enum):
    TCP = 0
    UDP = 1

class IPerfCommand(Command):
    def __init__(self, targets: list[str], transport: TransportProtocol, received_bytes: int,
                 jitter_alert: float, loss_alert: float, bandwidth_alert: float):
        self.targets = targets
        self.transport = transport
        self.received_bytes = received_bytes
        self.jitter_alert = jitter_alert
        self.loss_alert = loss_alert
        self.bandwidth_alert = bandwidth_alert

    def serialize(self) -> bytes:
        targets_bytes = b'\0'.join([target.encode('utf-8') for target in self.targets])
        transport_bytes = self.transport.value.to_bytes(1, byteorder='big')
        bytes_bytes = self.received_bytes.to_bytes(8, 'big')
        jitter_alert_bytes = struct.pack('>d', self.jitter_alert)
        loss_alert_bytes = struct.pack('>d', self.loss_alert)
        bandwidth_alert_bytes = struct.pack('>d', self.bandwidth_alert)

        return b''.join([bytes_bytes, jitter_alert_bytes, loss_alert_bytes,
                        bandwidth_alert_bytes, transport_bytes, targets_bytes])

    @classmethod
    def deserialize(cls, data: bytes) -> Self:
        bytes_val = int.from_bytes(data[:8], 'big')
        jitter_alert = struct.unpack('>d', data[8:16])[0]
        loss_alert = struct.unpack('>d', data[16:24])[0]
        bandwidth_alert = struct.unpack('>d', data[24:32])[0]
        transport = TransportProtocol(int.from_bytes(data[32:33], 'big'))
        targets = [target.decode('utf-8') for target in data[33:].split(b'\0')]

        return cls(targets=targets, transport=transport,
                   received_bytes=bytes_val, jitter_alert=jitter_alert,
                    loss_alert=loss_alert, bandwidth_alert=bandwidth_alert)
