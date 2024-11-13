import struct
from enum import Enum
from typing import Any

class TransportProtocol(Enum):
    TCP = 0
    UDP = 1


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

class PingCommand(Command):
    def __init__(self, targets: list[str], count: int, rtt_alert: float):
        self.targets = targets
        self.count = count
        self.rtt_alert = rtt_alert

    def serialize(self) -> bytes:
        count_bytes = self.count.to_bytes(8, 'big')
        rtt_alert_bytes = struct.pack('>d', self.rtt_alert)
        targets_bytes = b'\0'.join([target.encode('utf-8') for target in self.targets])
        return b''.join([count_bytes, rtt_alert_bytes, targets_bytes])

    @classmethod
    def deserialize(cls: Any, data: bytes) -> 'PingCommand':
        count = int.from_bytes(data[:8], 'big')
        rtt_alert = struct.unpack('>d', data[8:16])[0]
        targets = [target.decode('utf-8') for target in data[16:].split(b'\0')]

        return cls(targets=targets, count=count, rtt_alert=rtt_alert)

class IPerfCommand(Command):
    def __init__(self, targets: list[str], transport: TransportProtocol, received_bytes: int,
                 jitter_alert: float, loss_alert: float, bandwidth_alert: float):
        self.targets = targets
        self.transport = transport
        self.received_bytes = received_bytes
        self.jitter_alert = jitter_alert
        self.loss_alert = loss_alert
        self.bandwidth_alert = bandwidth_alert

    def serialize(self) -> bytes:
        targets_bytes = b'\0'.join([target.encode('utf-8') for target in self.targets])
        transport_bytes = self.transport.value.to_bytes(1, byteorder='big')
        bytes_bytes = self.received_bytes.to_bytes(8, 'big')
        jitter_alert_bytes = struct.pack('>d', self.jitter_alert)
        loss_alert_bytes = struct.pack('>d', self.loss_alert)
        bandwidth_alert_bytes = struct.pack('>d', self.bandwidth_alert)

        return b''.join([bytes_bytes, jitter_alert_bytes, loss_alert_bytes,
                        bandwidth_alert_bytes, transport_bytes, targets_bytes])

    @classmethod
    def deserialize(cls: Any, data: bytes) -> 'IPerfCommand':
        bytes_val = int.from_bytes(data[:8], 'big')
        jitter_alert = struct.unpack('>d', data[8:16])[0]
        loss_alert = struct.unpack('>d', data[16:24])[0]
        bandwidth_alert = struct.unpack('>d', data[24:32])[0]
        transport = TransportProtocol(int.from_bytes(data[32:33], 'big'))
        targets = [target.decode('utf-8') for target in data[33:].split(b'\0')]

        return cls(targets=targets, transport=transport,
                   received_bytes=bytes_val, jitter_alert=jitter_alert,
                    loss_alert=loss_alert, bandwidth_alert=bandwidth_alert)


class IPCommand(Command):
    def __init__(self, targets: list[str], alert_down: bool):
        self.targets = targets
        self.alert_down = alert_down

    def serialize(self) -> bytes:
        targets_bytes = b'\0'.join([target.encode('utf-8') for target in self.targets])
        alert_down_bytes = struct.pack('>d', self.alert_down)
        return b''.join([alert_down_bytes, targets_bytes])

    @classmethod
    def deserialize(cls: Any, data: bytes) -> 'IPCommand':
        alert_down = struct.unpack('>d', data[:1])[0]
        targets = [target.decode('utf-8') for target in data[1:].split(b'\0')]
        return cls(targets=targets, alert_down=alert_down)

class SystemMonitorCommand(Command):
    def __init__(self, targets: list[str], cpu_alert: float, memory_alert: float):
        self.targets = targets
        self.cpu_alert = cpu_alert
        self.memory_alert = memory_alert

    def serialize(self) -> bytes:
        targets_bytes = b'\0'.join([target.encode('utf-8') for target in self.targets])
        cpu_alert_bytes = struct.pack('>d', self.cpu_alert)
        memory_alert_bytes = struct.pack('>d', self.memory_alert)

        return b''.join([cpu_alert_bytes, memory_alert_bytes, targets_bytes])

    @classmethod
    def deserialize(cls: Any, data: bytes) -> 'SystemMonitorCommand':
        cpu_alert = struct.unpack('>d', data[:8])[0]
        memory_alert = struct.unpack('>d', data[8:16])[0]
        targets = [target.decode('utf-8') for target in data[16:].split(b'\0')]

        return cls(targets=targets, cpu_alert=cpu_alert, memory_alert=memory_alert)
