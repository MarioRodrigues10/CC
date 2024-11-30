from abc import ABC, abstractmethod
from typing import Self, cast

from .Message import SerializationException

class NetTaskSegmentBody(ABC):
    @abstractmethod
    def _body_serialize(self) -> bytes:
        pass

    def serialize(self) -> bytes:
        for i, command_class in enumerate(NetTaskSegmentBody.__subclasses__()):
            if isinstance(self, command_class):
                command_type_bytes = i.to_bytes(1, 'big')
                command_contents_bytes = self._body_serialize()

                return command_type_bytes + command_contents_bytes

        raise SerializationException('Unknown segment type')

    @classmethod
    @abstractmethod
    def deserialize(cls, data: bytes) -> Self:
        if len(data) <= 1:
            raise SerializationException('Incomplete command')

        try:
            command_type = int.from_bytes(data[:1], 'big')
            command_class = cast(Self, NetTaskSegmentBody.__subclasses__()[command_type])
            return command_class.deserialize(data[1:])
        except IndexError as e:
            raise SerializationException('Unknown segment type') from e
