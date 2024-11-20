import struct
from typing import Any, Self

from .Message import Message

class PingOutput(Message):
    def __init__(self, target: str, avg_latency: float, stdev_latency: float):
        self.target = target
        self.avg_latency = avg_latency
        self.stdev_latency = stdev_latency

    def _message_serialize(self) -> bytes:
        avg_latency_bytes = struct.pack('>f', self.avg_latency)
        stdev_latency_bytes = struct.pack('>f', self.stdev_latency)
        target_bytes = self.target.encode('utf-8')

        return b''.join([avg_latency_bytes, stdev_latency_bytes, target_bytes])

    @classmethod
    def deserialize(cls, data: bytes) -> Self:
        avg_latency = struct.unpack('>d', data[:4])[0]
        stdev_latency = struct.unpack('>d', data[4:8])[0]
        target = data[8:].decode('utf-8')

        return cls(target, avg_latency, stdev_latency)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, PingOutput):
            return \
                self.target == other.target and \
                self.avg_latency == other.avg_latency and \
                self.stdev_latency == other.stdev_latency

        return False

    def __str__(self) -> str:
        return 'PingOutput(' \
            f'target={self.target}, ' \
            f'avg_latency={self.avg_latency}, ' \
            f'stdev_latency={self.stdev_latency})'
