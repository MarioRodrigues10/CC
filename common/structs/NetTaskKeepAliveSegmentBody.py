from typing import Any, Self

from .Message import SerializationException
from .NetTaskSegmentBody import NetTaskSegmentBody

class NetTaskKeepAliveSegmentBody(NetTaskSegmentBody):
    def __init__(self) -> None:
        pass

    def _body_serialize(self) -> bytes:
        return b''

    @classmethod
    def deserialize(cls, data: bytes) -> Self:
        if len(data) != 0:
            raise SerializationException('Invalid NetTaskKeepAliveSegmentBody')
        return cls()

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, NetTaskKeepAliveSegmentBody):
            return True
        return False

    def __repr__(self) -> str:
        return 'NetTaskKeepAliveSegmentBody()'
