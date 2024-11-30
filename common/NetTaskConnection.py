import time
from typing import Optional
from .structs.NetTaskSegment import NetTaskSegment

INITIAL_ESTIMATED_RTT = 2 # seconds

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

        self.message_sent_times: dict[int, float] = {}
        self.last_message_time = time.time()
        self.estimated_rtt = None
        self.estimated_rtt_stdev = None

    def __retransmit(self, sequence: int) -> Optional[NetTaskSegment]:
        to_retransmit = self.unacknowledged_segments.get(sequence)
        if to_retransmit is None:
            pass

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
        self.last_message_time = time.time()

        if segment.sequence == 0:
            print('ACK', segment.acknowledgment)

            # ACK segment
            if segment.acknowledgment > self.other_highest_acknowledgment:
                self.other_highest_acknowledgment = segment.acknowledgment

                for sequence in list(self.unacknowledged_segments):
                    if sequence <= segment.acknowledgment:
                        del self.unacknowledged_segments[sequence]

                if segment.acknowledgment in self.message_sent_times:
                    rtt = self.last_message_time - self.message_sent_times[segment.acknowledgment]

                    if self.estimated_rtt is None:
                        self.estimated_rtt = rtt
                        self.estimated_rtt_stdev = rtt
                    else:
                        self.estimated_rtt_stdev = \
                            0.75 * self.estimated_rtt_stdev + 0.25 * abs(rtt - self.estimated_rtt)
                        self.estimated_rtt = 0.875 * self.estimated_rtt + 0.125 * rtt

                for sequence in list(self.message_sent_times):
                    if sequence <= segment.acknowledgment:
                        del self.message_sent_times[sequence]
            else:
                retransmit_segment = self.__retransmit(segment.acknowledgment + 1)
                if retransmit_segment is not None:
                    send_segments.append(retransmit_segment)
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
        self.message_sent_times[self.send_sequence] = time.time()
        self.send_sequence += 1
        return segment

    def __retransmission_timeout(self) -> float:
        if self.estimated_rtt is None:
            return INITIAL_ESTIMATED_RTT
        else:
            return self.estimated_rtt * 4 + self.estimated_rtt_stdev

    def time_until_next_timeout(self) -> float:
        return self.__retransmission_timeout()

    def send_if_timed_out(self) -> Optional[NetTaskSegment]:
        delta_time = time.time() - self.last_message_time

        if len(self.unacknowledged_segments) > 0 and delta_time > self.__retransmission_timeout():
            print('Retransmitting via timeout', 'RTT', self.estimated_rtt)
            retransmit_sequence = self.other_highest_acknowledgment + 1

            if retransmit_sequence in self.message_sent_times:
                del self.message_sent_times[retransmit_sequence]

            return self.__retransmit(retransmit_sequence)

        return None
