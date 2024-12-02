import struct
from typing import Any, Self

from .Message import SerializationException
from .NetTaskSegmentBody import NetTaskSegmentBody

class NetTaskSegment:
    def __init__(self, sequence: int, time: float, host: str, body: NetTaskSegmentBody):
        self.sequence = sequence
        self.time = time
        self.host = host
        self.body = body

    def serialize(self) -> bytes:
        sequence_bytes = self.sequence.to_bytes(4, 'big')
        time_bytes = struct.pack('>d', self.time)
        host_bytes = self.host.encode('utf-8') + b'\0'
        body_bytes = self.body.serialize()

        return b''.join([sequence_bytes, time_bytes, host_bytes, body_bytes])

    @classmethod
    def deserialize(cls, data: bytes) -> Self:
        if len(data) <= 13:
            raise SerializationException('Incomplete NetTaskSegment')

        try:
            sequence = int.from_bytes(data[:4], 'big')
            time = struct.unpack('>d', data[4:12])[0]

            host_end = data.index(b'\0', 12)
            host = data[12:host_end].decode('utf-8')

            body = NetTaskSegmentBody.deserialize(data[host_end + 1:])
        except (UnicodeError, ValueError) as e:
            raise SerializationException() from e

        return cls(sequence, time, host, body)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, NetTaskSegment):
            return \
                self.sequence == other.sequence and \
                self.host == other.host and \
                self.time == other.time and \
                self.body == other.body

        return False

    def __repr__(self) -> str:
        return 'NetTaskSegment(' \
            f'sequence={self.sequence}, ' \
            f'host={self.host}, ' \
            f'time={self.time}, ' \
            f'body={self.body})'
