import struct
from enum import Enum
from typing import Any

from common.structs.PingCommand import PingCommand
from common.structs.IPerfCommand import IPerfCommand
from common.structs.IPCommand import IPCommand
from common.structs.SystemMonitorCommand import SystemMonitorCommand

class CommandType(Enum):
    PING = 1
    IPERF = 2
    IP = 3
    SYSTEM_MONITOR = 4

class Command:
    @classmethod
    def deserialize(cls: Any, data: bytes) -> Any:
        command_type = CommandType(int.from_bytes(data[:1], 'big'))
        if command_type == CommandType.PING:
            return PingCommand.deserialize(data[1:])
        elif command_type == CommandType.IPERF:
            return IPerfCommand.deserialize(data[1:])
        elif command_type == CommandType.IP:
            return IPCommand.deserialize(data[1:])
        elif command_type == CommandType.SYSTEM_MONITOR:
            return SystemMonitorCommand.deserialize(data[1:])
        else:
            raise ValueError('Unknown command type')
