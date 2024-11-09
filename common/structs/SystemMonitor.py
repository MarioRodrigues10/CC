class SystemMonitor:
    SCALE = 1_000_000

    def __init__(self, cpu: float, memory: float):
        self.cpu = cpu
        self.memory = memory
    
    def serialize(self) -> bytes:
        cpu_bytes = int(self.cpu * self.SCALE).to_bytes(8, 'big', signed=True)
        memory_bytes = int(self.memory * self.SCALE).to_bytes(8, 'big')
        return b"".join([cpu_bytes, memory_bytes])
    
    def deserialize(cls, data: bytes):
        cpu = int.from_bytes(data[:8], 'big') / cls.SCALE
        memory = int.from_bytes(data[8:], 'big') / cls.SCALE
        return cls(cpu=cpu, memory=memory)
    