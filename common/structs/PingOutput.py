import struct

class PingOutput:
    def __init__(self, avg_latency: float, std_dev_latency: float):
        self.avg_latency = avg_latency
        self.std_dev_latency = std_dev_latency

    def serialize(self) -> bytes:
        avg_latency_bytes = struct.pack('>d', self.avg_latency)
        std_dev_latency_bytes = struct.pack('>d', self.std_dev_latency)
        return b''.join([avg_latency_bytes, std_dev_latency_bytes])

    def deserialize(self, cls, data: bytes) -> 'PingOutput':
        avg_latency = struct.unpack('>d', data[:8])[0]
        std_dev_latency = struct.unpack('>d', data[8:16])[0]
        return cls(avg_latency=avg_latency, std_dev_latency=std_dev_latency)
