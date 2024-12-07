from typing import Any, Self

from .Message import Message, SerializationException

class MessageTasksRequest(Message):
    def __init__(self) -> None:
        pass

    def _message_serialize(self) -> bytes:
        return b''

    @classmethod
    def deserialize(cls, data: bytes) -> Self:
        if len(data) != 0:
            raise SerializationException('Incorrect MessageTasksRequest length')
        return cls()

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, MessageTasksRequest)

    def __repr__(self) -> str:
        return 'MessageTasksRequest()'
