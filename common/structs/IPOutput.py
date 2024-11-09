class IPOutput:
    SCALE = 1_000_000

    def __init__(self, interfaceName: str, connectivity: str, txBytes: int, txPackets: int, rxBytes: int, rxPackets: int):
        self.interfaceName = interfaceName
        self.connectivity = connectivity
        self.txBytes = txBytes
        self.txPackets = txPackets
        self.rxBytes = rxBytes
        self.rxPackets = rxPackets
    
    def serialize(self) -> bytes:
        interfaceName_bytes = self.interfaceName.encode('utf-8')
        connectivity_bytes = self.connectivity.encode('utf-8')
        txBytes_bytes = self.txBytes.to_bytes(8, 'big')
        txPackets_bytes = self.txPackets.to_bytes(8, 'big')
        rxBytes_bytes = self.rxBytes.to_bytes(8, 'big')
        rxPackets_bytes = self.rxPackets.to_bytes(8, 'big')
        return b"".join([interfaceName_bytes, connectivity_bytes, txBytes_bytes, txPackets_bytes, rxBytes_bytes, rxPackets_bytes])
    
    def deserialize(cls, data: bytes):
        interfaceName, connectivity, txBytes, txPackets, rxBytes, rxPackets = data.split(b',')
        
        interfaceName = interfaceName.decode('utf-8')
        connectivity = connectivity.decode('utf-8')
        txBytes = int.from_bytes(txBytes, 'big') 
        txPackets = int.from_bytes(txPackets, 'big')
        rxBytes = int.from_bytes(rxBytes, 'big')
        rxPackets = int.from_bytes(rxPackets, 'big')
        
        return cls(interfaceName=interfaceName, connectivity=connectivity, txBytes=txBytes, txPackets=txPackets, rxBytes=rxBytes, rxPackets=rxPackets)