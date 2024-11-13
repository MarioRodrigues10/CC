import struct

class PingOutput:
    def __init__(self, avgLatency: float, stdDevLatency: float):
        self.avgLatency = avgLatency
        self.stdDevLatency = stdDevLatency

    def serialize(self) -> bytes:
        avgLatency_bytes = struct.pack('>d', self.avgLatency)
        stdDevLatency_bytes = struct.pack('>d', self.stdDevLatency)
        return b''.join([avgLatency_bytes, stdDevLatency_bytes])
    
    def deserialize(cls, data: bytes):
        avgLatency = struct.unpack('>d', data[:8])[0]
        stdDevLatency = struct.unpack('>d', data[8:16])[0]
        return cls(avgLatency=avgLatency, stdDevLatency=stdDevLatency)