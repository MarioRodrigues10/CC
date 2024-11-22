from abc import ABC, abstractmethod
from typing import Self, cast

class SerializationException(Exception):
    pass

class Message(ABC):
    @abstractmethod
    def _message_serialize(self) -> bytes:
        pass

    def serialize(self) -> bytes:
        for i, message_class in enumerate(Message.__subclasses__()):
            if isinstance(self, message_class):
                command_type_bytes = i.to_bytes(1, 'big')
                command_contents_bytes = self._message_serialize()

                return command_type_bytes + command_contents_bytes

        raise SerializationException('Unknown message type')

    @classmethod
    @abstractmethod
    def deserialize(cls, data: bytes) -> Self:
        if len(data) == 0:
            raise SerializationException('Incomplete message')

        try:
            message_type = int.from_bytes(data[:1], 'big')
            message_class = cast(type[Self], Message.__subclasses__()[message_type])
            return message_class.deserialize(data[1:])
        except IndexError as e:
            raise SerializationException('Unknown message type') from e
