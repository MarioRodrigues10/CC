class MessagePrepare:
    def __init__(self, iperf_tcp: bool, iperf_udp: bool):
        self.iperf_tcp = iperf_tcp
        self.iperf_udp = iperf_udp

    def serialize(self) -> bytes:
        iperf_tcp_bytes = int(self.iperf_tcp).to_bytes(1, 'big')
        iperf_udp_bytes = int(self.iperf_udp).to_bytes(1, 'big')
        return b''.join([iperf_tcp_bytes, iperf_udp_bytes])

    def deserialize(self, cls, data: bytes) -> 'MessagePrepare':
        iperf_tcp = bool(int.from_bytes(data[0:1], 'big'))
        iperf_udp = bool(int.from_bytes(data[1:2], 'big'))

        return cls(iperf_tcp=iperf_tcp, iperf_udp=iperf_udp)
