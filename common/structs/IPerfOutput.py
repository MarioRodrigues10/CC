class IPerfOutput:
    SCALE = 1_000_000 

    def __init__(self, jitter: float, bandwidth: float, loss: float):
        self.jitter = jitter
        self.bandwidth = bandwidth
        self.loss = loss

    def serialize(self) -> bytes:
        jitter_bytes = int(self.jitter * self.SCALE).to_bytes(8, 'big', signed=True)
        bandwidth_bytes = int(self.bandwidth * self.SCALE).to_bytes(8, 'big')
        loss_bytes = int(self.loss * self.SCALE).to_bytes(8, 'big')
        return b"".join([jitter_bytes, bandwidth_bytes, loss_bytes])

    def deserialize(cls, data: bytes):
        jitter = int.from_bytes(data[:8], 'big') / cls.SCALE
        bandwidth = int.from_bytes(data[8:16], 'big') / cls.SCALE
        loss = int.from_bytes(data[16:], 'big') / cls.SCALE
        return cls(jitter=jitter, bandwidth=bandwidth, loss=loss)
