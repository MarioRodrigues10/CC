from typing import Any, Self

from .Message import Message

class MessagePrepare(Message):
    def __init__(self, iperf_tcp: bool, iperf_udp: bool):
        self.iperf_tcp = iperf_tcp
        self.iperf_udp = iperf_udp

    def _message_serialize(self) -> bytes:
        integer = 2 * int(self.iperf_udp) + int(self.iperf_tcp)
        return integer.to_bytes(1, 'big')

    @classmethod
    def deserialize(cls, data: bytes) -> Self:
        integer = int.from_bytes(data, 'big')
        iperf_tcp = bool(integer & 1)
        iperf_udp = bool(integer & 2)

        return cls(iperf_tcp, iperf_udp)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, MessagePrepare):
            return \
                self.iperf_tcp == other.iperf_tcp and \
                self.iperf_udp == other.iperf_udp

        return False

    def __str__(self) -> str:
        return 'MessagePrepare(' \
            f'iperf_tcp={self.iperf_tcp}, ' \
            f'iperf_udp={self.iperf_udp})'
