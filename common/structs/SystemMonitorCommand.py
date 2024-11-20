import struct
from typing import Any, Self

from common.structs.Command import Command

class SystemMonitorCommand(Command):
    def __init__(self, targets: list[str], cpu_alert: float, memory_alert: float):
        self.targets = targets
        self.cpu_alert = cpu_alert
        self.memory_alert = memory_alert

    def _command_serialize(self) -> bytes:
        targets_bytes = b'\0'.join([target.encode('utf-8') for target in self.targets])
        cpu_alert_bytes = struct.pack('>d', self.cpu_alert)
        memory_alert_bytes = struct.pack('>d', self.memory_alert)

        return b''.join([cpu_alert_bytes, memory_alert_bytes, targets_bytes])

    @classmethod
    def deserialize(cls, data: bytes) -> Self:
        cpu_alert = struct.unpack('>d', data[:8])[0]
        memory_alert = struct.unpack('>d', data[8:16])[0]
        targets = [target.decode('utf-8') for target in data[16:].split(b'\0')]

        return cls(targets=targets, cpu_alert=cpu_alert, memory_alert=memory_alert)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, SystemMonitorCommand):
            return \
                self.targets == other.targets and \
                self.cpu_alert == other.cpu_alert and \
                self.memory_alert == other.memory_alert

        return False

    def __str__(self) -> str:
        return 'SystemMonitorCommand(' \
            f'targets={self.targets}, ' \
            f'cpu_alert={self.cpu_alert}, ' \
            f'memory_alert={self.memory_alert})'
