import re
import subprocess
from typing import Any, Self

from .Command import Command, CommandException
from .IPOutput import IPOutput
from .Message import SerializationException

class IPCommand(Command):
    def __init__(self, targets: list[str], alert_down: bool):
        self.targets = targets
        self.alert_down = alert_down

    def run(self) -> dict[str, IPOutput]:
        results = {}
        for interface in self.targets:
            try:
                process = subprocess.run(['ip', '-s', 'link', 'show', interface],
                                         capture_output=True,
                                         check=True)
                stdout = process.stdout.decode('utf-8')
            except (OSError, subprocess.SubprocessError) as e:
                raise CommandException('ip exited with non-0 exit code!') from e
            except UnicodeDecodeError as e:
                raise CommandException() from e

            status = stdout.find(' UP ') != -1
            stdout = '\n'.join(stdout.split('\n')[2:]) # Skip first two lines
            value_matches = [int(v) for v in re.findall(r'[0-9]+', stdout)]

            try:
                rx_bytes = value_matches[0]
                rx_packets = value_matches[1]
                tx_bytes = value_matches[6]
                tx_packets = value_matches[7]
            except IndexError as e:
                raise CommandException('Invalid ip command output!') from e

            results[interface] = \
                IPOutput(interface, status, tx_bytes, tx_packets, rx_bytes, rx_packets)

        return results

    def should_emit_alert(self, command_output: Any) -> bool:
        if not isinstance(command_output, IPOutput):
            raise CommandException('Incorrect command output type')

        return self.alert_down and not command_output.connectivity

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
