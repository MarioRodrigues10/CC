import socket

from sys import stderr
from threading import Condition, Thread
from typing import Any, Callable, Optional, Self, TypeVar

from .NetTaskConnection import NetTaskConnection, NetTaskConnectionException
from .structs.Message import SerializationException
from .structs.NetTaskSegment import NetTaskSegment

class NetTaskRuntimeException(Exception):
    pass

T = TypeVar('T')

# Check socket for periodical retransmissions in case connection beggining gets lost
MINIMAL_SOCKET_TIMEOUT = 2

class NetTask:
    def __init__(self, own_host_name: str, bind_port: Optional[int] = None):
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.__own_host_name = own_host_name
        self.__is_server = bind_port is not None
        if self.__is_server:
            self.__socket.bind(('0.0.0.0', bind_port))

        self.__host_addr_port: dict[str, tuple[str, int]] = {}
        self.__connections: dict[str, NetTaskConnection] = {}

        self.__condition = Condition()
        self.__bg_thread = Thread(target = self.__bg_loop)
        self.__bg_thread.daemon = True
        self.__bg_thread.start()

    @staticmethod
    def __synchronized(f: Callable[..., T]) -> Callable[..., T]:
        def wrapper(self: Self, *args: Any) -> T:
            # pylint: disable=protected-access
            with self.__condition:
                if not self.__bg_thread.is_alive():
                    raise NetTaskRuntimeException('Management thread died unexpectedly')
                return f(self, *args)

        return wrapper

    def __receive_next_segment(self) -> tuple[NetTaskSegment, str]:
        while True:
            segment_bytes, addr_port = self.__socket.recvfrom(1 << 16)
            try:
                segment = NetTaskSegment.deserialize(segment_bytes)

                with self.__condition:
                    self.__host_addr_port[segment.host] = addr_port
                    if segment.host not in self.__connections:
                        self.__connections[segment.host] = \
                            NetTaskConnection(self.__own_host_name, False)

                return segment, segment.host
            except SerializationException:
                print('NetTask ignored deserialization exception', file=stderr)

    def __handle_received_segment(self, segment: NetTaskSegment, host: str) -> None:
        connection = self.__connections[host]

        reply_segments = connection.handle_received_segment(segment)
        for reply_segment in reply_segments:
            addr_port = self.__host_addr_port[host]
            self.__socket.sendto(reply_segment.serialize(), addr_port)

        self.__condition.notify_all()

    def __handle_timeout(self) -> None:
        for host, connection in list(self.__connections.items()):
            try:
                wakeup_segment = connection.act_on_timeout()

                if wakeup_segment is not None:
                    addr_port = self.__host_addr_port[host]
                    self.__socket.sendto(wakeup_segment.serialize(), addr_port)
            except NetTaskConnectionException as e:
                if self.__is_server:
                    print('NetTask connection closed unexpectedly', file=stderr)
                    del self.__connections[host]
                else:
                    raise e

    def __time_until_next_timeout(self) -> Optional[float]:
        try:
            min_connections = min(c.time_until_next_timeout() for c in self.__connections.values())
            return min(MINIMAL_SOCKET_TIMEOUT, min_connections)
        except ValueError:
            return MINIMAL_SOCKET_TIMEOUT

    def __bg_loop(self) -> None:
        while True:
            self.__socket.settimeout(self.__time_until_next_timeout())

            try:
                segment, host = self.__receive_next_segment()
                with self.__condition:
                    try:
                        self.__handle_received_segment(segment, host)
                    except BaseException as e:
                        self.__condition.notify_all()
                        raise e

            except TimeoutError:
                with self.__condition:
                    try:
                        self.__handle_timeout()
                    except BaseException as e:
                        self.__condition.notify_all()
                        raise e

    @__synchronized
    def connect(self, host: str, addr_port: tuple[str, int]) -> None:
        self.__host_addr_port[host] = addr_port
        if host not in self.__connections:
            self.__connections[host] = NetTaskConnection(self.__own_host_name, True)

            connect_segment = self.__connections[host].prepare_connect_segment()
            self.__socket.sendto(connect_segment.serialize(), addr_port)

            while True:
                # Avoid deadlock in case of death of the management thread
                if not self.__bg_thread.is_alive():
                    raise NetTaskRuntimeException('Management thread died unexpectedly')

                if host not in self.__connections:
                    raise NetTaskRuntimeException('Connection died unexpectedly')

                if self.__connections[host].is_connected():
                    return
                self.__condition.wait()
        else:
            raise NetTaskRuntimeException(f'Already connected to {host}')

    @__synchronized
    def receive(self) -> tuple[list[bytes], str]:
        while True:
            # Avoid deadlock in case of death of the management thread
            if not self.__bg_thread.is_alive():
                raise NetTaskRuntimeException('Management thread died unexpectedly')

            for connection_host, connection in self.__connections.items():
                messages, window_segment = connection.get_received_messages()
                if window_segment is not None:
                    addr_port = self.__host_addr_port[connection_host]
                    self.__socket.sendto(window_segment.serialize(), addr_port)

                if messages != []:
                    return messages, connection_host

            self.__condition.wait()

    @__synchronized
    def send(self, message: bytes, host: str) -> None:
        while True:
            # Avoid deadlock in case of death of the management thread
            if not self.__bg_thread.is_alive():
                raise NetTaskRuntimeException('Management thread died unexpectedly')

            if host not in self.__connections:
                raise NetTaskRuntimeException('Connection died unexpectedly')

            # Try to at least enqueue the segment for transmission
            connection = self.__connections[host]
            try:
                segments = connection.encapsulate_for_sending(message)

                for segment in segments:
                    # Receiver's window is not full and segment can be transmitted now
                    addr_port = self.__host_addr_port[host]
                    self.__socket.sendto(segment.serialize(), addr_port)
                    return
            except NetTaskConnectionException:
                # Full send queue
                pass

            self.__condition.wait()
