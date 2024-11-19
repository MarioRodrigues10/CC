import struct
from typing import Self

from common.structs.Command import Command

class PingCommand(Command):
    def __init__(self, targets: list[str], count: int, rtt_alert: float):
        self.targets = targets
        self.count = count
        self.rtt_alert = rtt_alert

    def _command_serialize(self) -> bytes:
        count_bytes = self.count.to_bytes(8, 'big')
        rtt_alert_bytes = struct.pack('>d', self.rtt_alert)
        targets_bytes = b'\0'.join([target.encode('utf-8') for target in self.targets])
        return b''.join([count_bytes, rtt_alert_bytes, targets_bytes])

    @classmethod
    def _command_deserialize(cls, data: bytes) -> Self:
        count = int.from_bytes(data[:8], 'big')
        rtt_alert = struct.unpack('>d', data[8:16])[0]
        targets = [target.decode('utf-8') for target in data[16:].split(b'\0')]

        return cls(targets=targets, count=count, rtt_alert=rtt_alert)
