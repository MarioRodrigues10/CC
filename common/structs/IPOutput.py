class IPOutput:
    def __init__(self, interface_name: str, connectivity: bool, txBytes: int, txPackets: int, rxBytes: int, rxPackets: int):
        self.interface_name = interface_name
        self.connectivity = connectivity
        self.txBytes = txBytes
        self.txPackets = txPackets
        self.rxBytes = rxBytes
        self.rxPackets = rxPackets
    
    def serialize(self) -> bytes:
        interface_name_bytes = self.interfaceName.encode('utf-8')
        connectivity_bytes = self.connectivity.to_bytes(1, 'big')
        txBytes_bytes = self.txBytes.to_bytes(8, 'big')
        txPackets_bytes = self.txPackets.to_bytes(8, 'big')
        rxBytes_bytes = self.rxBytes.to_bytes(8, 'big')
        rxPackets_bytes = self.rxPackets.to_bytes(8, 'big')
        return b''.join([txBytes_bytes, txPackets_bytes, rxBytes_bytes, rxPackets_bytes, connectivity_bytes, interface_name_bytes])
    
    def deserialize(cls, data: bytes):
        txBytes = int.from_bytes(data[:8], 'big')
        txPackets = int.from_bytes(data[8:16], 'big')
        rxBytes = int.from_bytes(data[16:24], 'big')
        rxPackets = int.from_bytes(data[24:32], 'big')
        connectivity = data[32:33].decode('utf-8')
        interface_name = data[33:].decode('utf-8')
        
        return cls(interfaceName=interface_name, connectivity=connectivity, txBytes=txBytes, txPackets=txPackets, rxBytes=rxBytes, rxPackets=rxPackets)