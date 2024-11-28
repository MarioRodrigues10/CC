from .structs.NetTaskSegment import NetTaskSegment

class NetTaskConnection:
    def __init__(self) -> None:
        self.queue: list[NetTaskSegment] = []
        self.send_sequence = 0

    def enqueue(self, segment: NetTaskSegment) -> None:
        self.queue.append(segment)

    def can_receive(self) -> bool:
        return len(self.queue) != 0

    def receive(self) -> bytes:
        return self.queue.pop(0).message

    def send(self, message: bytes, host: str) -> NetTaskSegment:
        ret = NetTaskSegment(self.send_sequence, host, message)
        self.send_sequence += 1
        return ret
