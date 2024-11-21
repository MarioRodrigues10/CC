from typing import Any, Self

from .Message import Message, SerializationException

class IPOutput(Message):
    # pylint: disable-next=too-many-arguments disable-next=too-many-positional-arguments
    def __init__(self, interface_name: str, connectivity: bool, tx_bytes: int,
                 tx_packets: int, rx_bytes: int, rx_packets: int):
        self.interface_name = interface_name
        self.connectivity = connectivity
        self.tx_bytes = tx_bytes
        self.tx_packets = tx_packets
        self.rx_bytes = rx_bytes
        self.rx_packets = rx_packets

    def _message_serialize(self) -> bytes:
        interface_name_bytes = self.interface_name.encode('utf-8')
        connectivity_bytes = int(self.connectivity).to_bytes(1, 'big')
        tx_bytes_bytes = self.tx_bytes.to_bytes(8, 'big')
        tx_packets_bytes = self.tx_packets.to_bytes(8, 'big')
        rx_bytes_bytes = self.rx_bytes.to_bytes(8, 'big')
        rx_packets_bytes = self.rx_packets.to_bytes(8, 'big')

        return b''.join([tx_bytes_bytes, tx_packets_bytes, rx_bytes_bytes, rx_packets_bytes,
                        connectivity_bytes, interface_name_bytes])

    @classmethod
    def deserialize(cls, data: bytes) -> Self:
        if len(data) <= 33:
            raise SerializationException('Incomplete IPOutput message')

        try:
            tx_bytes = int.from_bytes(data[:8], 'big')
            tx_packets = int.from_bytes(data[8:16], 'big')
            rx_bytes = int.from_bytes(data[16:24], 'big')
            rx_packets = int.from_bytes(data[24:32], 'big')
            connectivity = bool(int.from_bytes(data[32:33], 'big'))
            interface_name = data[33:].decode('utf-8')
        except UnicodeDecodeError as e:
            raise SerializationException() from e

        return cls(interface_name, connectivity, tx_bytes, tx_packets, rx_bytes, rx_packets)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, IPOutput):
            return \
                self.interface_name == other.interface_name and \
                self.connectivity == other.connectivity and \
                self.tx_bytes == other.tx_bytes and \
                self.tx_packets == other.tx_packets and \
                self.rx_bytes == other.rx_bytes and \
                self.rx_packets == other.rx_packets

        return False

    def __repr__(self) -> str:
        return 'IPOutput(' \
            f'interface_name={self.interface_name}, ' \
            f'connectivity={self.connectivity}, ' \
            f'tx_bytes={self.tx_bytes}, ' \
            f'tx_packets={self.tx_packets}, ' \
            f'rx_bytes={self.rx_bytes}, ' \
            f'rx_packets={self.rx_packets})'
