import struct
from typing import Any, Self

from .Message import Message, SerializationException
from .Command import Command

class MessageTask(Message):
    def __init__(self, task_id: str, frequency: float, command: Command):
        self.task_id = task_id
        self.frequency = frequency
        self.command = command

    def _message_serialize(self) -> bytes:
        frequency_bytes = struct.pack('>f', self.frequency)
        task_id_bytes = self.task_id.encode('utf-8')
        command_bytes = self.command.serialize()

        return b''.join([frequency_bytes, task_id_bytes, b'\0', command_bytes])

    @classmethod
    def deserialize(cls, data: bytes) -> Self:
        if len(data) <= 5:
            raise SerializationException('Incomplete MessageTask')

        try:
            frequency = struct.unpack('>f', data[:4])[0]
            limit = data.index(b'\0', 4)
            task_id = data[4:limit].decode('utf-8')
            command = Command.deserialize(data[limit + 1:])
        except (struct.error, ValueError, UnicodeDecodeError) as e:
            raise SerializationException() from e

        return cls(task_id, frequency, command)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, MessageTask):
            return \
                self.task_id == other.task_id and \
                self.frequency == other.frequency and \
                self.command == other.command

        return False

    def __repr__(self) -> str:
        return 'MessageTask(' \
            f'task_id={self.task_id}, ' \
            f'frequency={self.frequency}, ' \
            f'command={self.command})'
