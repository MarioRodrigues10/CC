from typing import Any, Self

from .Message import Message

class MessageRegister(Message):
    def __init__(self, host_id: str):
        self.host_id = host_id

    def _message_serialize(self) -> bytes:
        id_bytes = self.host_id.encode('utf-8')
        return id_bytes

    @classmethod
    def deserialize(cls, data: bytes) -> Self:
        host_id = data.decode('utf-8')
        return cls(host_id)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, MessageRegister):
            return self.host_id == other.host_id

        return False

    def __str__(self) -> str:
        return f'MessageRegister(host_id={self.host_id})'
