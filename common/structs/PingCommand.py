import struct
from typing import Any, Self

from .Command import Command
from .Message import SerializationException

class PingCommand(Command):
    def __init__(self, targets: list[str], count: int, rtt_alert: float):
        self.targets = targets
        self.count = count
        self.rtt_alert = rtt_alert

    def _command_serialize(self) -> bytes:
        count_bytes = self.count.to_bytes(2, 'big')
        rtt_alert_bytes = struct.pack('>f', self.rtt_alert)
        targets_bytes = b'\0'.join([target.encode('utf-8') for target in self.targets])

        return b''.join([count_bytes, rtt_alert_bytes, targets_bytes])

    @classmethod
    def deserialize(cls, data: bytes) -> Self:
        if len(data) <= 6:
            raise SerializationException('Incomplete PingCommand')

        try:
            count = int.from_bytes(data[:2], 'big')
            rtt_alert = struct.unpack('>f', data[2:6])[0]
            targets = [target.decode('utf-8') for target in data[6:].split(b'\0')]
        except (struct.error, UnicodeDecodeError) as e:
            raise SerializationException() from e

        return cls(targets, count, rtt_alert)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, PingCommand):
            return \
                self.targets == other.targets and \
                self.count == other.count and \
                self.rtt_alert == other.rtt_alert

        return False

    def __repr__(self) -> str:
        return 'PingCommand(' \
            f'targets={self.targets}, ' \
            f'count={self.count}, ' \
            f'rtt_alert={self.rtt_alert})'
