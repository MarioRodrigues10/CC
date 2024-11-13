import struct
from typing import Any

class IPerfOutput:
    def __init__(self, jitter: float, bandwidth: float, loss: float):
        self.jitter = jitter
        self.bandwidth = bandwidth
        self.loss = loss

    def serialize(self) -> bytes:
        jitter_bytes = struct.pack('>d', self.jitter)
        bandwidth_bytes = struct.pack('>d', self.bandwidth)
        loss_bytes = struct.pack('>d', self.loss)
        return b''.join([jitter_bytes, bandwidth_bytes, loss_bytes])

    @classmethod
    def deserialize(cls: Any, data: bytes) -> 'IPerfOutput':
        jitter = struct.unpack('>d', data[:8])[0]
        bandwidth = struct.unpack('>d', data[8:16])[0]
        loss = struct.unpack('>d', data[16:24])[0]
        return cls(jitter=jitter, bandwidth=bandwidth, loss=loss)
