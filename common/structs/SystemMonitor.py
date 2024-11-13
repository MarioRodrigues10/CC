import struct
class SystemMonitor:
    def __init__(self, cpu: float, memory: float):
        self.cpu = cpu
        self.memory = memory

    def serialize(self) -> bytes:
        cpu_bytes = struct.pack('>d', self.cpu)
        memory_bytes = struct.pack('>d', self.memory)
        return b''.join([cpu_bytes, memory_bytes])

    def deserialize(self, cls, data: bytes) -> 'SystemMonitor':
        cpu = struct.unpack('>d', data[:8])[0]
        memory = struct.unpack('>d', data[8:16])[0]
        return cls(cpu=cpu, memory=memory)
