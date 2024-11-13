class IPOutput:
    def __init__(self, interface_name: str, connectivity: bool, tx_bytes: int,
                 tx_packets: int, rx_bytes: int, rx_packets: int):
        self.interface_name = interface_name
        self.connectivity = connectivity
        self.tx_bytes = tx_bytes
        self.tx_packets = tx_packets
        self.rx_bytes = rx_bytes
        self.rx_packets = rx_packets

    def serialize(self) -> bytes:
        interface_name_bytes = self.interface_name.encode('utf-8')
        connectivity_bytes = self.connectivity.to_bytes(1, 'big')
        tx_bytes_bytes = self.tx_bytes.to_bytes(8, 'big')
        tx_packets_bytes = self.tx_packets.to_bytes(8, 'big')
        rx_bytes_bytes = self.rx_bytes.to_bytes(8, 'big')
        rx_packets_bytes = self.rx_packets.to_bytes(8, 'big')
        return b''.join([tx_bytes_bytes, tx_packets_bytes, rx_bytes_bytes, rx_packets_bytes,
                        connectivity_bytes, interface_name_bytes])

    def deserialize(self, cls, data: bytes):
        tx_bytes = int.from_bytes(data[:8], 'big')
        tx_packets = int.from_bytes(data[8:16], 'big')
        rx_bytes = int.from_bytes(data[16:24], 'big')
        rx_packets = int.from_bytes(data[24:32], 'big')
        connectivity = data[32:33].decode('utf-8')
        interface_name = data[33:].decode('utf-8')

        return cls(interfaceName=interface_name, connectivity=connectivity, tx_bytes=tx_bytes,
                   tx_packets=tx_packets, rx_bytes=rx_bytes, rx_packets=rx_packets)
