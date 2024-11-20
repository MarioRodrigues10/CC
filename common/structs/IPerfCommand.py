import struct
from enum import Enum
from typing import Any, Self

from .Command import Command
from .Message import SerializationException

class TransportProtocol(Enum):
    TCP = 0
    UDP = 1

class IPerfCommand(Command):
    def __init__(self, targets: list[str], transport: TransportProtocol, time: float,
                 jitter_alert: float, loss_alert: float, bandwidth_alert: float):

        self.targets = targets
        self.transport = transport
        self.time = time
        self.jitter_alert = jitter_alert
        self.loss_alert = loss_alert
        self.bandwidth_alert = bandwidth_alert

    def _command_serialize(self) -> bytes:
        targets_bytes = b'\0'.join([target.encode('utf-8') for target in self.targets])
        transport_bytes = self.transport.value.to_bytes(1, byteorder='big')
        time_bytes = struct.pack('>f', self.time)
        jitter_alert_bytes = struct.pack('>f', self.jitter_alert)
        loss_alert_bytes = struct.pack('>f', self.loss_alert)
        bandwidth_alert_bytes = struct.pack('>f', self.bandwidth_alert)

        return b''.join([transport_bytes, time_bytes, jitter_alert_bytes, loss_alert_bytes,
                        bandwidth_alert_bytes, targets_bytes])

    @classmethod
    def deserialize(cls, data: bytes) -> Self:
        if len(data) <= 17:
            raise SerializationException('Incomplete IPerfCommand command')

        try:
            transport = TransportProtocol(int.from_bytes(data[:1], 'big'))
            time = struct.unpack('>f', data[1:5])[0]
            jitter_alert = struct.unpack('>f', data[5:9])[0]
            loss_alert = struct.unpack('>f', data[9:13])[0]
            bandwidth_alert = struct.unpack('>f', data[13:17])[0]
            targets = [target.decode('utf-8') for target in data[17:].split(b'\0')]
        except (ValueError, struct.error, UnicodeDecodeError) as e:
            raise SerializationException() from e

        return cls(targets, transport, time, jitter_alert, loss_alert, bandwidth_alert)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, IPerfCommand):
            return \
                self.targets == other.targets and \
                self.transport == other.transport and \
                self.time == other.time and \
                self.jitter_alert == other.jitter_alert and \
                self.loss_alert == other.loss_alert and \
                self.bandwidth_alert == other.bandwidth_alert

        return False

    def __str__(self) -> str:
        return 'IPerfCommand(' \
            f'targets={self.targets}, ' \
            f'transport={self.transport}, ' \
            f'time={self.time}, ' \
            f'jitter_alert={self.jitter_alert}, ' \
            f'loss_alert={self.loss_alert}, ' \
            f'bandwidth_alert={self.bandwidth_alert})'
