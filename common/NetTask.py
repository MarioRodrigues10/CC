import socket

from sys import stderr
from threading import Condition, Thread
from typing import Any, Callable, Optional, Self, TypeVar

from .NetTaskConnection import NetTaskConnection
from .structs.Message import SerializationException
from .structs.NetTaskSegment import NetTaskSegment

class NetTaskRuntimeException(Exception):
    pass

T = TypeVar('T')

class NetTask:
    def __init__(self, own_host_name: str, bind_port: Optional[int] = None):
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.__own_host_name = own_host_name
        if bind_port is not None:
            self.__socket.bind(('0.0.0.0', bind_port))

        self.__condition = Condition()
        self.__bg_thread = Thread(target = self.__bg_loop)
        self.__bg_thread.daemon = True
        self.__bg_thread.start()

        self.__host_addr_port: dict[str, tuple[str, int]] = {}
        self.__connections: dict[str, NetTaskConnection] = {}

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
                        self.__connections[segment.host] = NetTaskConnection(self.__own_host_name)

                return segment, segment.host
            except SerializationException:
                print('NetTask ignored deserialization exception', file=stderr)

    def __handle_received_segment(self, segment: NetTaskSegment, host: str) -> None:
        connection = self.__connections[host]

        reply_segment = connection.handle_received_segment(segment)
        if reply_segment is not None:
            addr_port = self.__host_addr_port[host]
            self.__socket.sendto(reply_segment.serialize(), addr_port)

        self.__condition.notify_all()

    def __bg_loop(self) -> None:
        while True:
            segment, host = self.__receive_next_segment()
            with self.__condition:
                self.__handle_received_segment(segment, host)

    @__synchronized
    def connect(self, host: str, addr_port: tuple[str, int]) -> None:
        self.__host_addr_port[host] = addr_port
        if host not in self.__connections:
            self.__connections[host] = NetTaskConnection(self.__own_host_name)

        # TODO - establish connection

    @__synchronized
    def receive(self) -> tuple[bytes, str]:
        while True:
            # Avoid deadlock in case of death of the management thread
            if not self.__bg_thread.is_alive():
                raise NetTaskRuntimeException('Management thread died unexpectedly')

            for connection_host, connection in self.__connections.items():
                message = connection.get_next_received_message()
                if message is not None:
                    return message, connection_host

            self.__condition.wait()

    @__synchronized
    def send(self, message: bytes, host: str) -> None:
        addr_port = self.__host_addr_port[host]
        connection = self.__connections[host]

        segment = connection.encapsulate_for_sending(message)
        self.__socket.sendto(segment.serialize(), addr_port)
