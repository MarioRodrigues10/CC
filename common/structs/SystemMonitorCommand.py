import struct
from typing import Any, Self

from .Command import Command
from .Message import SerializationException

class SystemMonitorCommand(Command):
    def __init__(self, cpu_alert: float, memory_alert: float):
        self.cpu_alert = cpu_alert
        self.memory_alert = memory_alert

    def _command_serialize(self) -> bytes:
        cpu_alert_bytes = struct.pack('>f', self.cpu_alert)
        memory_alert_bytes = struct.pack('>f', self.memory_alert)

        return b''.join([cpu_alert_bytes, memory_alert_bytes])

    @classmethod
    def deserialize(cls, data: bytes) -> Self:
        if len(data) != 8:
            raise SerializationException('Incorrect SystemMonitorCommand length')

        try:
            cpu_alert = struct.unpack('>f', data[:4])[0]
            memory_alert = struct.unpack('>f', data[4:8])[0]
        except struct.error as e:
            raise SerializationException() from e

        return cls(cpu_alert, memory_alert)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, SystemMonitorCommand):
            return \
                self.cpu_alert == other.cpu_alert and \
                self.memory_alert == other.memory_alert

        return False

    def __repr__(self) -> str:
        return 'SystemMonitorCommand(' \
            f'cpu_alert={self.cpu_alert}, ' \
            f'memory_alert={self.memory_alert})'
