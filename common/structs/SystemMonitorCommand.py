import os
import re
import struct
import time
from typing import Any, Self

from .Command import Command, CommandException
from .Message import SerializationException
from .SystemMonitorOutput import SystemMonitorOutput

CPU_MEASUREMENT_TIME = 1 # seconds

class SystemMonitorCommand(Command):
    def __init__(self, cpu_alert: float, memory_alert: float):
        self.cpu_alert = cpu_alert
        self.memory_alert = memory_alert

    def __measure_cpu_usage(self) -> float:
        def measure_usage_ticks() -> int:
            try:
                with open('/proc/stat', 'r', encoding='utf-8') as f:
                    proc_stat_contents = f.read()

                return int(proc_stat_contents.split()[4])
            except (OSError, UnicodeDecodeError) as e:
                raise CommandException('Failed to read CPU information file!') from e
            except (ValueError, IndexError) as e:
                raise CommandException('Invalid CPU information file contents!') from e

        try:
            cpu_count = os.sysconf('SC_NPROCESSORS_CONF')
            cpu_time_unit = os.sysconf('SC_CLK_TCK') # (1 / cpu_time_unit) seconds
            if cpu_time_unit == 0:
                raise ValueError()
        except ValueError as e:
            raise CommandException('CPU measurement operation unsupported by the OS!') from e

        initial_time_measurement = time.time()
        initial_usage_measurement = measure_usage_ticks()
        time.sleep(CPU_MEASUREMENT_TIME)
        final_time_measurement = time.time()
        final_usage_measurement = measure_usage_ticks()

        time_delta = (final_time_measurement - initial_time_measurement) * cpu_count
        usage_delta = (final_usage_measurement - initial_usage_measurement) / cpu_time_unit
        return (1 - usage_delta / time_delta) * 100.0

    def __measure_memory_usage(self) -> float:
        try:
            with open('/proc/meminfo', 'r', encoding='utf-8') as f:
                proc_meminfo_contents = f.read()
        except (OSError, UnicodeDecodeError) as e:
            raise CommandException('Failed to read memory information file!') from e

        key_value_matches = re.findall(r'^([A-Za-z]+):\s*([0-9]+)',
                                       proc_meminfo_contents,
                                       flags=re.MULTILINE)
        memory_values = { key: int(value) for key, value in key_value_matches }

        try:
            absolute_memory_usage = memory_values['MemTotal']     \
                                  + memory_values['Shmem']        \
                                  - memory_values['MemFree']      \
                                  - memory_values['Buffers']      \
                                  - memory_values['Cached']       \
                                  - memory_values['SReclaimable']
            relative_memory_usage = absolute_memory_usage / memory_values['MemTotal']
        except (KeyError, ZeroDivisionError) as e:
            raise CommandException('Invalid memory information file contents!') from e

        return relative_memory_usage * 100.0

    def run(self) -> SystemMonitorOutput:
        return SystemMonitorOutput(self.__measure_cpu_usage(), self.__measure_memory_usage())

    def should_emit_alert(self, command_output: Any) -> bool:
        if not isinstance(command_output, SystemMonitorOutput):
            raise CommandException('Incorrect command output type')

        return command_output.cpu >= self.cpu_alert or command_output.memory >= self.memory_alert

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
