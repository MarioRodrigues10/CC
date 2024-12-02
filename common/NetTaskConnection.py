import time
from typing import Optional

from .structs.NetTaskSegment import NetTaskSegment
from .structs.NetTaskSegmentBody import NetTaskSegmentBody
from .structs.NetTaskAckSegmentBody import NetTaskAckSegmentBody
from .structs.NetTaskCloseSegmentBody import NetTaskCloseSegmentBody
from .structs.NetTaskDataSegmentBody import NetTaskDataSegmentBody
from .structs.NetTaskKeepAliveSegmentBody import NetTaskKeepAliveSegmentBody
from .structs.NetTaskWindowSegmentBody import NetTaskWindowSegmentBody

INITIAL_TIMEOUT = 5 # seconds
MINIMUM_TIMEOUT = 0.005 # seconds (needed to avoid busy waiting on localhost)
RETRANSMISSION_PENALIZATION = 1.25 # times original RTT estimation

KEEP_ALIVE_INTERVAL = 10 # seconds
KEEP_ALIVE_TIMEOUT = 30 # seconds

WINDOW_SIZE = 32 # messages
INFORM_NEW_MAX_SEQUENCE_THRESHOLD = 24 # messages
SEND_QUEUE_MAX_SIZE = 64 # messages

class NetTaskConnectionException(Exception):
    pass

# pylint: disable-next=too-many-instance-attributes
class NetTaskConnection:
    def __init__(self, own_host_name: str, is_starter: bool):
        current_time = time.time()

        # Basic information
        self.__own_host_name = own_host_name
        self.__is_starter = is_starter

        # Incoming data
        self.__receive_queue: dict[int, NetTaskSegment] = {}
        self.__next_sequence_to_receive = 1
        self.__own_max_ack = 0
        self.__last_known_other_alive = current_time

        # Outgoing data
        self.__unacked_segments: dict[int, NetTaskSegment] = {}
        self.__next_sequence_to_send = 1
        self.__other_max_ack = 0
        self.__last_sent_data_segment_time = current_time
        self.__last_made_aware_alive = current_time

        # RTT estimation
        self.__rtt_avg_estimate: Optional[float] = None
        self.__rtt_stdev_estimate: Optional[float] = None

        # Flow control information
        self.__send_queue: list[bytes] = []
        self.__own_max_sequence = self.__next_sequence_to_receive + WINDOW_SIZE
        self.__other_max_sequence = 0
        self.__messages_removed_from_receive_queue = 0

        # Connection closing
        self.__other_has_closed = False
        self.__own_close_segment_sequence: Optional[int] = None

    def __register_segment(self, segment: NetTaskSegment) -> None:
        if segment.sequence < self.__next_sequence_to_receive:
            return

        if not isinstance(segment.body, NetTaskDataSegmentBody):
            self.__own_max_sequence += 1

        if segment.sequence <= self.__own_max_sequence:
            self.__receive_queue[segment.sequence] = segment

    def __handle_received_ackable_segment(self, segment: NetTaskSegment) -> list[NetTaskSegment]:
        segments: list[NetTaskSegment] = []

        # Fail if connection started incorrectly
        if self.__own_max_ack == 0 and \
            (segment.sequence != 1 or not isinstance(segment.body, NetTaskWindowSegmentBody)):

            raise NetTaskConnectionException('Connection started unexpectedly')

        # Register segment in receive queue if possible
        self.__register_segment(segment)

        # Calculate and send next ACK
        while True:
            self.__own_max_ack += 1
            if self.__own_max_ack not in self.__receive_queue:
                self.__own_max_ack -= 1
                break

        self.__last_made_aware_alive = time.time()
        segments.append(NetTaskSegment(0,
                                       segment.time,
                                       self.__own_host_name,
                                       NetTaskAckSegmentBody(self.__own_max_ack)))

        # Reply to connection beginning
        if isinstance(segment.body, NetTaskWindowSegmentBody):
            self.__other_max_sequence = segment.body.max_sequence

            if self.__next_sequence_to_send == 1:
                segments.append(self.__update_connection_on_send(
                    NetTaskWindowSegmentBody(self.__own_max_sequence)))

        # Reply to connection end
        if isinstance(segment.body, NetTaskCloseSegmentBody):
            self.__other_has_closed = True

            if self.__own_close_segment_sequence is None:
                close_segment = self.__update_connection_on_send(
                    NetTaskCloseSegmentBody())

                self.__own_close_segment_sequence = close_segment.sequence
                segments.append(close_segment)

        return segments

    def __handle_received_ack_segment(self, ack: int, seg_time: float) -> list[NetTaskSegment]:
        segments: list[NetTaskSegment] = []

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
        if ack < self.__next_sequence_to_send - 1 and \
            ack <= self.__other_max_ack and \
            ack + 1 in self.__unacked_segments:

            self.__last_sent_data_segment_time = current_time
            self.__unacked_segments[ack + 1].time = current_time
            self.__last_made_aware_alive = current_time
            segments.append(self.__unacked_segments[ack + 1])
        else:
            self.__other_max_ack = ack

        # Transmit more segments if possible
        segments += self.__sendable_segments()

        return segments

    def handle_received_segment(self, segment: NetTaskSegment) -> list[NetTaskSegment]:
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

            if len(self.__unacked_segments) > 0 and \
                self.__other_max_ack + 1 in self.__unacked_segments:

                if self.__rtt_avg_estimate is not None and self.__rtt_stdev_estimate is not None:
                    self.__rtt_avg_estimate *= RETRANSMISSION_PENALIZATION
                    self.__rtt_stdev_estimate *= RETRANSMISSION_PENALIZATION ** 0.5

                retransmit_segment = self.__unacked_segments[self.__other_max_ack + 1]
                retransmit_segment.time = current_time
                self.__last_sent_data_segment_time = current_time
                return retransmit_segment

        # Periodically send keep-alives to avoid timing out the other side
        if self.__is_starter and \
            self.__own_max_ack > 0 and \
            self.__own_close_segment_sequence is None and \
            current_time - self.__last_made_aware_alive >= KEEP_ALIVE_INTERVAL:

            return self.__update_connection_on_send(NetTaskKeepAliveSegmentBody())

        return None

    def prepare_connect_segment(self) -> NetTaskSegment:
        return self.__update_connection_on_send(NetTaskWindowSegmentBody(self.__own_max_sequence))

    def is_connected(self) -> bool:
        return \
            self.__next_sequence_to_send >= 2 and \
            self.__own_max_ack >= 1 and \
            not self.is_closed()

    def get_received_messages(self) -> tuple[list[bytes], Optional[NetTaskSegment]]:
        messages = []
        window_segment = None

        while self.__next_sequence_to_receive in self.__receive_queue:
            segment = self.__receive_queue.pop(self.__next_sequence_to_receive)
            if isinstance(segment.body, NetTaskDataSegmentBody):
                messages.append(segment.body.message)
                self.__own_max_sequence += 1
                self.__messages_removed_from_receive_queue += 1

            self.__next_sequence_to_receive += 1

        if self.__messages_removed_from_receive_queue >= INFORM_NEW_MAX_SEQUENCE_THRESHOLD and \
            messages:

            self.__messages_removed_from_receive_queue = 0
            window_segment = self.__update_connection_on_send(
                NetTaskWindowSegmentBody(self.__own_max_sequence))

        return messages, window_segment

    def __update_connection_on_send(self, body: NetTaskSegmentBody) -> NetTaskSegment:
        current_time = time.time()

        segment = NetTaskSegment(self.__next_sequence_to_send,
                                 current_time,
                                 self.__own_host_name,
                                 body)

        self.__unacked_segments[segment.sequence] = segment
        self.__next_sequence_to_send += 1
        self.__last_sent_data_segment_time = current_time
        self.__last_made_aware_alive = current_time

        return segment

    def __sendable_segments(self) -> list[NetTaskSegment]:
        can_send = \
            self.__other_max_sequence - self.__next_sequence_to_send - len(self.__unacked_segments)

        to_send = self.__send_queue[:can_send]
        self.__send_queue = self.__send_queue[len(to_send) + 1:]
        return [self.__update_connection_on_send(NetTaskDataSegmentBody(m)) for m in to_send]

    def encapsulate_for_sending(self, message: bytes) -> list[NetTaskSegment]:
        if len(self.__send_queue) == SEND_QUEUE_MAX_SIZE:
            raise NetTaskConnectionException('Full send queue')

        self.__send_queue.append(message)
        return self.__sendable_segments()

    def is_closed(self) -> bool:
        return \
            self.__other_has_closed and \
            self.__own_close_segment_sequence is not None and \
            self.__own_close_segment_sequence not in self.__unacked_segments

    def close(self) -> Optional[NetTaskSegment]:
        if len(self.__unacked_segments) > 0:
            return None

        if self.__own_close_segment_sequence is not None:
            return None

        close_segment = self.__update_connection_on_send(NetTaskCloseSegmentBody())
        self.__own_close_segment_sequence = close_segment.sequence
        return close_segment
