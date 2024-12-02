from typing import Any, Self

from .NetTaskSegmentBody import NetTaskSegmentBody

class NetTaskDataSegmentBody(NetTaskSegmentBody):
    def __init__(self, message: bytes):
        self.message = message

    def _body_serialize(self) -> bytes:
        return self.message

    @classmethod
    def deserialize(cls, data: bytes) -> Self:
        return cls(data)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, NetTaskDataSegmentBody):
            return self.message == other.message

        return False

    def __repr__(self) -> str:
        return f'NetTaskDataSegmentBody(message={self.message!r})'
