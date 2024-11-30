from typing import Any, Self

from .Message import SerializationException
from .NetTaskSegmentBody import NetTaskSegmentBody

class NetTaskAckSegmentBody(NetTaskSegmentBody):
    def __init__(self, ack: int):
        self.ack = ack

    def _body_serialize(self) -> bytes:
        return self.ack.to_bytes(4, 'big')

    @classmethod
    def deserialize(cls, data: bytes) -> Self:
        if len(data) != 4:
            raise SerializationException('Invalid NetTaskAckSegmentBody')

        ack = int.from_bytes(data)
        return cls(ack)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, NetTaskAckSegmentBody):
            return self.ack == other.ack

        return False

    def __repr__(self) -> str:
        return f'NetTaskAckSegmentBody(ack={self.ack})'
