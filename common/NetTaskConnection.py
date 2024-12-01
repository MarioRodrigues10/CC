import time
from typing import Optional

from .structs.NetTaskSegment import NetTaskSegment
from .structs.NetTaskDataSegmentBody import NetTaskDataSegmentBody
from .structs.NetTaskAckSegmentBody import NetTaskAckSegmentBody
from .structs.NetTaskKeepAliveSegmentBody import NetTaskKeepAliveSegmentBody

INITIAL_TIMEOUT = 5 # seconds
MINIMUM_TIMEOUT = 0.005 # seconds (needed to avoid busy waiting on localhost)
RETRANSMISSION_PENALIZATION = 1.25 # times original RTT estimation

KEEP_ALIVE_INTERVAL = 10 # seconds
KEEP_ALIVE_TIMEOUT = 30 # seconds

class NetTaskConnectionException(Exception):
    pass

class NetTaskConnection:
    # pylint: disable-next=too-many-instance-attributes
    def __init__(self, own_host_name: str, is_starter: bool):
        current_time = time.time()

        self.__own_host_name = own_host_name
        self.__is_starter = is_starter

        self.__receive_queue: dict[int, NetTaskSegment] = {}
        self.__next_sequence_to_receive = 1
        self.__own_max_ack = 0
        self.__last_known_other_alive = current_time

        self.__unacked_segments: dict[int, NetTaskSegment] = {}
        self.__next_sequence_to_send = 1
        self.__other_max_ack = 0
        self.__last_sent_data_segment_time = current_time
        self.__last_made_aware_alive = current_time

        self.__rtt_avg_estimate: Optional[float] = None
        self.__rtt_stdev_estimate: Optional[float] = None

    def __handle_received_ackable_segment(self, segment: NetTaskSegment) -> NetTaskSegment:
        if segment.sequence >= self.__next_sequence_to_receive:
            self.__receive_queue[segment.sequence] = segment

            # Calculate and send next ACK
            while True:
                self.__own_max_ack += 1
                if self.__own_max_ack not in self.__receive_queue:
                    self.__own_max_ack -= 1
                    break

        current_time = time.time()
        self.__last_made_aware_alive = current_time
        return NetTaskSegment(0,
                              segment.time,
                              self.__own_host_name,
                              NetTaskAckSegmentBody(self.__own_max_ack))

    def __handle_received_ack_segment(self, ack: int, seg_time: float) -> Optional[NetTaskSegment]:
        # Remove segments we know don't need to be retransmitted
        for sequence in list(self.__unacked_segments):
            if sequence <= ack:
                del self.__unacked_segments[sequence]

        # Update RTT estimate
        current_time = time.time()
        delta = current_time - seg_time
        if self.__rtt_avg_estimate is None or self.__rtt_stdev_estimate is None:
            self.__rtt_stdev_estimate = delta
            self.__rtt_avg_estimate = delta
        else:
            self.__rtt_stdev_estimate = \
                0.75 * self.__rtt_stdev_estimate + 0.25 * abs(delta - self.__rtt_avg_estimate)
            self.__rtt_avg_estimate = 0.875 * self.__rtt_avg_estimate + 0.125 * delta

        # Retranmsit if needed
        if ack < self.__next_sequence_to_send - 1 and ack <= self.__other_max_ack:
            self.__last_sent_data_segment_time = current_time
            self.__unacked_segments[ack + 1].time = current_time
            self.__last_made_aware_alive = current_time
            return self.__unacked_segments[ack + 1]
        else:
            self.__other_max_ack = ack
            return None

    def handle_received_segment(self, segment: NetTaskSegment) -> Optional[NetTaskSegment]:
        self.__last_known_other_alive = time.time()
        if isinstance(segment.body, NetTaskAckSegmentBody):
            return self.__handle_received_ack_segment(segment.body.ack, segment.time)
        else:
            return self.__handle_received_ackable_segment(segment)

    def __retransmission_time_limit(self) -> float:
        if self.__rtt_avg_estimate is None or self.__rtt_stdev_estimate is None:
            return INITIAL_TIMEOUT
        else:
            return self.__rtt_avg_estimate + 4 * max(self.__rtt_stdev_estimate, MINIMUM_TIMEOUT)

    def time_until_next_timeout(self) -> float:
        current_time = time.time()

        ack_timeout_time = \
            self.__retransmission_time_limit() - \
            (current_time - self.__last_sent_data_segment_time)

        keep_alive_interval_time = \
            KEEP_ALIVE_INTERVAL - (current_time - self.__last_made_aware_alive)

        keep_alive_timeout_time = \
            KEEP_ALIVE_TIMEOUT - (current_time - self.__last_known_other_alive)

        min_timeout = min(ack_timeout_time, keep_alive_interval_time, keep_alive_timeout_time)
        return max(min_timeout, MINIMUM_TIMEOUT)

    def act_on_timeout(self) -> Optional[NetTaskSegment]:
        current_time = time.time()

        # Fail if there is no reply from the other side in a long time
        if current_time - self.__last_known_other_alive >= KEEP_ALIVE_TIMEOUT:
            raise NetTaskConnectionException('Keep-alive timed out')

        # Retransmit segment if time to receive ACK passed
        if current_time - self.__last_sent_data_segment_time >= self.__retransmission_time_limit():
            self.__last_sent_data_segment_time = current_time

            if len(self.__unacked_segments) > 0:
                if self.__rtt_avg_estimate is not None and self.__rtt_stdev_estimate is not None:
                    self.__rtt_avg_estimate *= RETRANSMISSION_PENALIZATION
                    self.__rtt_stdev_estimate *= RETRANSMISSION_PENALIZATION ** 0.5

                retransmit_segment = self.__unacked_segments[self.__other_max_ack + 1]
                retransmit_segment.time = current_time
                self.__last_sent_data_segment_time = current_time
                return retransmit_segment

        # Periodically send keep-alives to avoid timing out the other side
        if self.__is_starter and current_time - self.__last_made_aware_alive >= KEEP_ALIVE_INTERVAL:
            keep_alive = NetTaskSegment(self.__next_sequence_to_send,
                                        current_time,
                                        self.__own_host_name,
                                        NetTaskKeepAliveSegmentBody())

            self.__update_connection_on_send(keep_alive)
            return keep_alive

        return None

    def get_next_received_message(self) -> Optional[bytes]:
        if self.__next_sequence_to_receive not in self.__receive_queue:
            return None

        to_receive = self.__receive_queue.pop(self.__next_sequence_to_receive)
        self.__next_sequence_to_receive += 1

        if isinstance(to_receive.body, NetTaskDataSegmentBody):
            return to_receive.body.message
        else:
            return self.get_next_received_message()

    def __update_connection_on_send(self, segment: NetTaskSegment) -> None:
        current_time = time.time()

        self.__unacked_segments[segment.sequence] = segment
        self.__next_sequence_to_send += 1
        self.__last_sent_data_segment_time = current_time
        self.__last_made_aware_alive = current_time

    def encapsulate_for_sending(self, message: bytes) -> NetTaskSegment:
        segment = NetTaskSegment(self.__next_sequence_to_send,
                                 time.time(),
                                 self.__own_host_name,
                                 NetTaskDataSegmentBody(message))

        self.__update_connection_on_send(segment)
        return segment
