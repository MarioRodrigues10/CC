from .structs.NetTaskSegment import NetTaskSegment

class NetTaskConnectionException(Exception):
    pass

class NetTaskConnection:
    def __init__(self, host: str):
        self.host = host

        self.receive_queue: dict[int, NetTaskSegment] = {}
        self.own_highest_acknowledgment = 0
        self.next_to_receive = 1

        self.unacknowledged_segments: dict[int, NetTaskSegment] = {}
        self.other_highest_acknowledgment = 0
        self.send_sequence = 1

    def __retransmit(self, sequence: int) -> NetTaskSegment:
        to_retransmit = self.unacknowledged_segments.get(sequence)
        if to_retransmit is None:
            raise NetTaskConnectionException()

        return to_retransmit

    def __next_own_highest_acknowledgment(self) -> int:
        ret = self.own_highest_acknowledgment
        while True:
            ret += 1
            if ret not in self.receive_queue:
                break

        return ret - 1

    def enqueue(self, segment: NetTaskSegment) -> list[NetTaskSegment]:
        send_segments = []

        if segment.sequence == 0:
            # ACK segment
            if segment.acknowledgment > self.other_highest_acknowledgment:
                self.other_highest_acknowledgment = segment.acknowledgment

                for sequence in list(self.unacknowledged_segments):
                    if sequence <= segment.acknowledgment:
                        del self.unacknowledged_segments[sequence]
            else:
                send_segments.append(self.__retransmit(segment.acknowledgment + 1))
        else:
            # Data segment
            if segment.sequence >= self.next_to_receive:
                self.receive_queue[segment.sequence] = segment
                self.own_highest_acknowledgment = self.__next_own_highest_acknowledgment()
                send_segments.append(
                    NetTaskSegment(0, self.own_highest_acknowledgment, self.host, b''))

        return send_segments

    def can_receive(self) -> bool:
        return self.next_to_receive in self.receive_queue

    def receive(self) -> bytes:
        message = self.receive_queue.pop(self.next_to_receive).message
        self.next_to_receive += 1
        return message

    def send(self, message: bytes) -> NetTaskSegment:
        segment = \
            NetTaskSegment(self.send_sequence, self.own_highest_acknowledgment, self.host, message)
        self.unacknowledged_segments[self.send_sequence] = segment
        self.send_sequence += 1
        return segment
