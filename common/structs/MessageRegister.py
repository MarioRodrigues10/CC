from typing import Any, Self

from .Message import Message, SerializationException

class MessageRegister(Message):
    def __init__(self, host_id: str):
        self.host_id = host_id

    def _message_serialize(self) -> bytes:
        id_bytes = self.host_id.encode('utf-8')
        return id_bytes

    @classmethod
    def deserialize(cls, data: bytes) -> Self:
        if len(data) == 0:
            raise SerializationException('Incomplete MessagePrepare')

        try:
            host_id = data.decode('utf-8')
        except UnicodeDecodeError as e:
            raise SerializationException() from e

        return cls(host_id)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, MessageRegister):
            return self.host_id == other.host_id

        return False

    def __repr__(self) -> str:
        return f'MessageRegister(host_id={self.host_id})'
