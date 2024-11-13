import struct
from typing import Any
from common.structs.Command import Command

class MessageTask:
    def __init__(self, task_id: str, frequency: float, command: Any):
        self.task_id = task_id
        self.frequency = frequency
        self.command = command

    def serialize(self) -> bytes:
        task_id_bytes = self.task_id.encode('utf-8')
        frequency_bytes = struct.pack('>d', self.frequency)
        command_bytes = self.command.serialize()
        return b''.join([frequency_bytes, task_id_bytes, b'\0', command_bytes])

    def deserialize(self, cls: Any, data: bytes) -> 'MessageTask':
        frequency = struct.unpack('>d', data[:8])[0]
        limit = data.index(b'\0', 8)
        task_id = data[8:limit].decode('utf-8')
        command = Command.deserialize(data[limit + 1:])

        return cls(task_id=task_id, frequency=frequency, command=command)
