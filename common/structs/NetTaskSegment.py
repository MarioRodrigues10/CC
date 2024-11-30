from typing import Any, Self

from .Message import SerializationException

class NetTaskSegment:
    def __init__(self, sequence: int, acknowledgment: int, host: str, message: bytes):
        self.sequence = sequence
        self.acknowledgment = acknowledgment
        self.host = host
        self.message = message

    def serialize(self) -> bytes:
        sequence_bytes = self.sequence.to_bytes(4, 'big')
        acknowledgment_bytes = self.acknowledgment.to_bytes(4, 'big')
        host_bytes = self.host.encode('utf-8') + b'\0'

        return b''.join([sequence_bytes, acknowledgment_bytes, host_bytes, self.message])

    @classmethod
    def deserialize(cls, data: bytes) -> Self:
        if len(data) <= 4:
            raise SerializationException('Incomplete NetTaskSegment')

        try:
            sequence = int.from_bytes(data[:4], 'big')
            acknowledgment = int.from_bytes(data[4:8], 'big')

            host_end = data.index(b'\0', 8)
            host = data[8:host_end].decode('utf-8')

            message = data[host_end + 1:]
        except (UnicodeError, ValueError) as e:
            raise SerializationException() from e

        return cls(sequence, acknowledgment, host, message)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, NetTaskSegment):
            return \
                self.sequence == other.sequence and \
                self.acknowledgment == other.acknowledgment and \
                self.host == other.host and \
                self.message == other.message

        return False

    def __repr__(self) -> str:
        return 'NetTaskSegment(' \
            f'sequence={self.sequence}, ' \
            f'acknowledgment={self.acknowledgment}, ' \
            f'host={self.host}, ' \
            f'message={self.message!r})'
