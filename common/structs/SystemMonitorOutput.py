import struct
from typing import Any, Self

from .Message import Message

class SystemMonitorOutput(Message):
    def __init__(self, cpu: float, memory: float):
        self.cpu = cpu
        self.memory = memory

    def _message_serialize(self) -> bytes:
        cpu_bytes = struct.pack('>f', self.cpu)
        memory_bytes = struct.pack('>f', self.memory)

        return b''.join([cpu_bytes, memory_bytes])

    @classmethod
    def deserialize(cls, data: bytes) -> Self:
        cpu = struct.unpack('>f', data[:4])[0]
        memory = struct.unpack('>f', data[4:8])[0]

        return cls(cpu, memory)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, SystemMonitorOutput):
            return \
                self.cpu == other.cpu and \
                self.memory == other.memory

        return False

    def __str__(self) -> str:
        return 'SystemMonitorCommandOutput(' \
            f'cpu={self.cpu}, ' \
            f'memory={self.memory})'
