import re
import statistics
import struct
import subprocess
from typing import Any, Self

from .Command import Command, CommandException
from .Message import SerializationException
from .PingOutput import PingOutput

PING_MAXIMUM_TIME = 5 # seconds per ping

class PingCommand(Command):
    def __init__(self, targets: list[str], count: int, rtt_alert: float):
        self.targets = targets
        self.count = count
        self.rtt_alert = rtt_alert

    def run(self) -> dict[str, PingOutput]:
        results = {}
        for target in self.targets:
            ping_deadline = PING_MAXIMUM_TIME * self.count
            ping_command = ['ping', '-w', str(ping_deadline), '-Ac', str(self.count), target]

            try:
                process = subprocess.run(ping_command, capture_output=True, check=True)
                stdout = process.stdout.decode('utf-8')
            except (OSError, subprocess.SubprocessError) as e:
                raise CommandException('ping exited with non-0 exit code!') from e
            except UnicodeDecodeError as e:
                raise CommandException() from e

            time_matches = re.findall(r'time=([0-9]+(?:\.[0-9]+)?)', stdout)
            time_values = [ float(groups) for groups in time_matches ]

            try:
                avg = statistics.mean(time_values)
                stdev = statistics.stdev(time_values)
            except statistics.StatisticsError as e:
                raise CommandException('ping didn\'t received less than 2 replies!') from e

            results[target] = PingOutput(target, avg, stdev)

        return results

    def should_emit_alert(self, command_output: Any) -> bool:
        if not isinstance(command_output, PingOutput):
            raise CommandException('Incorrect command output type')

        return command_output.avg_latency >= self.rtt_alert

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
