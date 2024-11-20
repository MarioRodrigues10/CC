from typing import Any, Self

from .Command import Command
from .Message import SerializationException

class IPCommand(Command):
    def __init__(self, targets: list[str], alert_down: bool):
        self.targets = targets
        self.alert_down = alert_down

    def _command_serialize(self) -> bytes:
        alert_down_bytes = int(self.alert_down).to_bytes(1, 'big')
        targets_bytes = b'\0'.join([target.encode('utf-8') for target in self.targets])

        return b''.join([alert_down_bytes, targets_bytes])

    @classmethod
    def deserialize(cls, data: bytes) -> Self:
        if len(data) <= 1:
            raise SerializationException('Incomplete IPCommand')

        try:
            alert_down = bool(int.from_bytes(data[:1], 'big'))
            targets = [target.decode('utf-8') for target in data[1:].split(b'\0')]
        except UnicodeDecodeError as e:
            raise SerializationException() from e

        return cls(targets, alert_down)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, IPCommand):
            return \
                self.targets == other.targets and \
                self.alert_down == other.alert_down

        return False

    def __repr__(self) -> str:
        return 'SystemMonitorCommand(' \
            f'targets={self.targets}, ' \
            f'alert_down={self.alert_down})'
