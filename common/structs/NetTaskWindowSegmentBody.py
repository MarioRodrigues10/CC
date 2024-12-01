from typing import Any, Self

from .Message import SerializationException
from .NetTaskSegmentBody import NetTaskSegmentBody

class NetTaskWindowSegmentBody(NetTaskSegmentBody):
    def __init__(self, window: int):
        self.window = window

    def _body_serialize(self) -> bytes:
        return self.window.to_bytes(4, 'big')

    @classmethod
    def deserialize(cls, data: bytes) -> Self:
        if len(data) != 4:
            raise SerializationException('Invalid NetTaskWindowSegmentBody')

        window = int.from_bytes(data)
        return cls(window)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, NetTaskWindowSegmentBody):
            return self.window == other.window

        return False

    def __repr__(self) -> str:
        return f'NetTaskAckSegmentBody(window={self.window})'
