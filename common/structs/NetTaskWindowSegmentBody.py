from typing import Any, Self

from .Message import SerializationException
from .NetTaskSegmentBody import NetTaskSegmentBody

class NetTaskWindowSegmentBody(NetTaskSegmentBody):
    def __init__(self, max_sequence: int):
        self.max_sequence = max_sequence

    def _body_serialize(self) -> bytes:
        return self.max_sequence.to_bytes(4, 'big')

    @classmethod
    def deserialize(cls, data: bytes) -> Self:
        if len(data) != 4:
            raise SerializationException('Invalid NetTaskWindowSegmentBody')

        max_sequence = int.from_bytes(data)
        return cls(max_sequence)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, NetTaskWindowSegmentBody):
            return self.max_sequence == other.max_sequence

        return False

    def __repr__(self) -> str:
        return f'NetTaskAckSegmentBody(max_sequence={self.max_sequence})'
