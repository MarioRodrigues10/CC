from abc import ABC, abstractmethod
from typing import Self, cast

from .Message import SerializationException

class Command(ABC):
    @abstractmethod
    def _command_serialize(self) -> bytes:
        pass

    def serialize(self) -> bytes:
        for i, command_class in enumerate(Command.__subclasses__()):
            if isinstance(self, command_class):
                command_type_bytes = i.to_bytes(1, 'big')
                command_contents_bytes = self._command_serialize()

                return command_type_bytes + command_contents_bytes

        raise SerializationException('Unknown command type')

    @classmethod
    @abstractmethod
    def deserialize(cls, data: bytes) -> Self:
        if len(data) <= 1:
            raise SerializationException('Incomplete command')

        try:
            command_type = int.from_bytes(data[:1], 'big')
            command_class = cast(Self, Command.__subclasses__()[command_type])
            return command_class.deserialize(data[1:])
        except IndexError as e:
            raise SerializationException('Unknown command type') from e
