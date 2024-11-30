from typing import Optional

from .structs.NetTaskSegment import NetTaskSegment
from .structs.NetTaskDataSegmentBody import NetTaskDataSegmentBody

class NetTaskConnection:
    def __init__(self, own_host_name: str):
        self.__own_host_name = own_host_name

        self.__receive_queue: dict[int, bytes] = {}
        self.__next_sequence_to_receive: int = 0

        self.__unacked_segments: dict[int, NetTaskSegment] = {}
        self.__send_sequence = 0

    def __handle_received_data_segment(self, sequence: int, message: bytes) -> None:
        if sequence >= self.__next_sequence_to_receive:
            self.__receive_queue[sequence] = message

    def handle_received_segment(self, segment: NetTaskSegment) -> None:
        if isinstance(segment.body, NetTaskDataSegmentBody):
            self.__handle_received_data_segment(segment.sequence, segment.body.message)

    def get_next_received_message(self) -> Optional[bytes]:
        if self.__next_sequence_to_receive not in self.__receive_queue:
            return None

        to_receive = self.__receive_queue.pop(self.__next_sequence_to_receive)
        self.__next_sequence_to_receive += 1
        return to_receive

    def encapsulate_for_sending(self, message: bytes) -> NetTaskSegment:
        segment = NetTaskSegment(self.__send_sequence,
                                 self.__own_host_name,
                                 NetTaskDataSegmentBody(message))

        self.__unacked_segments[segment.sequence] = segment
        self.__send_sequence += 1

        return segment
