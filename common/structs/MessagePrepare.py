class MessagePrepare:
    def __init__(self, iperfTCP: bool, iperfUDP: bool):
        self.iperfTCP = iperfTCP
        self.iperfUDP = iperfUDP

    def serialize(self) -> bytes:
        iperfTCP_bytes = self.iperfTCP.to_bytes(1, 'big')
        iperfUDP_bytes = self.iperfUDP.to_bytes(1, 'big')
        return b"".join([iperfTCP_bytes, iperfUDP_bytes])

    def deserialize(cls, data: bytes):
        iperfTCP = bool.from_bytes(data[0], 'big')
        iperfUDP = bool.from_bytes(data[1], 'big')

        return cls(iperfTCP=iperfTCP, iperfUDP=iperfUDP)