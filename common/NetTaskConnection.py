import time
from typing import Optional

from .structs.NetTaskSegment import NetTaskSegment
from .structs.NetTaskDataSegmentBody import NetTaskDataSegmentBody
from .structs.NetTaskAckSegmentBody import NetTaskAckSegmentBody

INITIAL_TIMEOUT = 5 # seconds

class NetTaskConnection:
    def __init__(self, own_host_name: str):
        self.__own_host_name = own_host_name

        self.__receive_queue: dict[int, bytes] = {}
        self.__next_sequence_to_receive = 1
        self.__own_max_ack = 0

        self.__unacked_segments: dict[int, NetTaskSegment] = {}
        self.__next_sequence_to_send = 1
        self.__other_max_ack = 0
        self.__last_sent_data_segment_time = time.time()

    def __handle_received_data_segment(self, sequence: int, message: bytes) \
        -> Optional[NetTaskSegment]:

        if sequence >= self.__next_sequence_to_receive:
            self.__receive_queue[sequence] = message

            # Calculate and send next ACK
            while True:
                self.__own_max_ack += 1
                if self.__own_max_ack not in self.__receive_queue:
                    self.__own_max_ack -= 1
                    break

        return NetTaskSegment(0,
                              self.__own_host_name,
                              NetTaskAckSegmentBody(self.__own_max_ack))

        return None

    def __handle_received_ack_segment(self, ack: int) -> Optional[NetTaskSegment]:
        print('ACK', ack)

        # Remove segments we know don't need to be retransmitted
        for sequence in list(self.__unacked_segments):
            if sequence <= ack:
                del self.__unacked_segments[sequence]

        # Retranmsit if needed
        if ack < self.__next_sequence_to_send - 1 and ack <= self.__other_max_ack:
            __last_sent_data_segment_time = time.time()
            return self.__unacked_segments[ack + 1]
        else:
            self.__other_max_ack = ack

        return None

    def handle_received_segment(self, segment: NetTaskSegment) -> Optional[NetTaskSegment]:
        if isinstance(segment.body, NetTaskDataSegmentBody):
            return self.__handle_received_data_segment(segment.sequence, segment.body.message)
        elif isinstance(segment.body, NetTaskAckSegmentBody):
            return self.__handle_received_ack_segment(segment.body.ack)

        return None

    def time_until_next_timeout(self) -> float:
        current_time = time.time()
        return max(INITIAL_TIMEOUT - (current_time - self.__last_sent_data_segment_time), 0.0)

    def act_on_timeout(self) -> Optional[NetTaskSegment]:
        current_time = time.time()
        if current_time - self.__last_sent_data_segment_time  >= INITIAL_TIMEOUT:
            self.__last_sent_data_segment_time  = current_time

            if len(self.__unacked_segments) > 0:
                retransmit_sequence = self.__other_max_ack + 1
                return self.__unacked_segments[retransmit_sequence]
        
        return None

    def get_next_received_message(self) -> Optional[bytes]:
        if self.__next_sequence_to_receive not in self.__receive_queue:
            return None

        to_receive = self.__receive_queue.pop(self.__next_sequence_to_receive)
        self.__next_sequence_to_receive += 1
        return to_receive

    def encapsulate_for_sending(self, message: bytes) -> NetTaskSegment:
        segment = NetTaskSegment(self.__next_sequence_to_send,
                                 self.__own_host_name,
                                 NetTaskDataSegmentBody(message))

        self.__unacked_segments[segment.sequence] = segment
        self.__next_sequence_to_send += 1
        self.__last_sent_data_segment_time = time.time()

        return segment
