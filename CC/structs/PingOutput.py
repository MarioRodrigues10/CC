class PingOutput:
    SCALE = 1_000_000

    def __init__(self, avgLatency: float, stdDevLatency: float):
        self.avgLatency = avgLatency
        self.stdDevLatency = stdDevLatency

    def serialize(self) -> bytes:
        avgLatency_bytes = int(self.avgLatency * self.SCALE).to_bytes(8, 'big', signed=True)
        stdDevLatency_bytes = int(self.stdDevLatency * self.SCALE).to_bytes(8, 'big')
        return b"".join([avgLatency_bytes, stdDevLatency_bytes])
    
    def deserialize(cls, data: bytes):
        avgLatency = int.from_bytes(data[:8], 'big') / cls.SCALE
        stdDevLatency = int.from_bytes(data[8:], 'big') / cls.SCALE
        return cls(avgLatency=avgLatency, stdDevLatency=stdDevLatency)