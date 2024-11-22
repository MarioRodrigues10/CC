from typing import Any, Self

from .Message import Message, SerializationException

class MessagePrepare(Message):
    def __init__(self) -> None:
        pass

    def _message_serialize(self) -> bytes:
        return b''

    @classmethod
    def deserialize(cls, data: bytes) -> Self:
        if len(data) != 0:
            raise SerializationException('Incorrect MessagePrepare length')
        return cls()

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, MessagePrepare)

    def __repr__(self) -> str:
        return 'MessagePrepare()'
