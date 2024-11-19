import struct
from typing import Self

from common.structs.Command import Command

class IPCommand(Command):
    def __init__(self, targets: list[str], alert_down: bool):
        self.targets = targets
        self.alert_down = alert_down

    def _command_serialize(self) -> bytes:
        targets_bytes = b'\0'.join([target.encode('utf-8') for target in self.targets])
        alert_down_bytes = struct.pack('>d', self.alert_down)
        return b''.join([alert_down_bytes, targets_bytes])

    @classmethod
    def deserialize(cls, data: bytes) -> Self:
        alert_down = struct.unpack('>d', data[:1])[0]
        targets = [target.decode('utf-8') for target in data[1:].split(b'\0')]
        return cls(targets=targets, alert_down=alert_down)
