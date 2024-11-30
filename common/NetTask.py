import socket
import sys
import time
from threading import Condition, Thread
from typing import Optional

from .NetTaskConnection import NetTaskConnectionException, NetTaskConnection
from .structs.NetTaskSegment import NetTaskSegment
from .structs.Message import SerializationException

INITIAL_ACK_WAIT_TIMING = 5

# pylint: disable-next=too-many-instance-attributes
class NetTask:
    def __init__(self, host: str, bind_port: Optional[int] = None):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.host = host
        self.bind_port = bind_port
        if bind_port is not None:
            self.socket.bind(('0.0.0.0', bind_port))

        self.condition = Condition()
        self.management_thread = Thread(target = self.__management_loop)
        self.management_thread.daemon = True
        self.management_thread.start()

        self.host_ips: dict[str, tuple[str, int]] = {}
        self.ip_hosts: dict[tuple[str, int], str] = {}
        self.connections: dict[str, NetTaskConnection] = {}

    def __del__(self) -> None:
        self.socket.close()

    def __next_segment(self) -> tuple[NetTaskSegment, tuple[str, int]]:
        while True:
            segment_bytes, addr_port = self.socket.recvfrom(1 << 16)
            try:
                return (NetTaskSegment.deserialize(segment_bytes), addr_port)
            except SerializationException:
                print('NetTask ignored deserialization exception', file=sys.stderr)

    def __assert_running_management_thread(self) -> None:
        if not self.management_thread.is_alive():
            raise NetTaskConnectionException('Connection ended')

    def add_host(self, host: str, addr_port: tuple[str, int]) -> None:
        with self.condition:
            self.__assert_running_management_thread()

            self.host_ips[host] = addr_port
            self.ip_hosts[addr_port] = host

            if host not in self.connections:
                self.connections[host] = NetTaskConnection(self.host)

    def remove_host(self, host: str) -> None:
        with self.condition:
            self.__assert_running_management_thread()

            addr_port = self.host_ips[host]

            del self.host_ips[host]
            del self.ip_hosts[addr_port]
            del self.connections[host]

    def __management_loop(self) -> None:
        self.socket.settimeout(INITIAL_ACK_WAIT_TIMING)

        while True:
            try:
                segment, addr_port = self.__next_segment()
            except TimeoutError:
                with self.condition:
                    # Retransmit ACKs
                    for host, connection in self.connections.items():
                        timeout_segment = connection.send_if_timed_out()
                        if timeout_segment is not None:
                            addr_port = self.host_ips[host]
                            self.socket.sendto(timeout_segment.serialize(), addr_port)

                continue

            with self.condition:
                self.add_host(segment.host, addr_port)
                connection = self.connections[segment.host]

                try:
                    to_send = connection.enqueue(segment)
                except NetTaskConnectionException:
                    self.remove_host(segment.host)

                    # Kill client if connection ended
                    if self.bind_port is None:
                        self.condition.notify_all()
                        return
                finally:
                    self.condition.notify_all()

                for segment in to_send:
                    self.socket.sendto(segment.serialize(), addr_port)

                wait = min(c.time_until_next_timeout() for c in self.connections.values())
                self.socket.settimeout(wait)

    def receive(self) -> tuple[bytes, str]:
        def get_receiving_host() -> Optional[str]:
            for host, connection in self.connections.items():
                if connection.can_receive():
                    return host

            return None

        with self.condition:
            while True:
                self.__assert_running_management_thread()

                host = get_receiving_host()
                if host is not None:
                    break

                self.condition.wait()

            return self.connections[host].receive(), host

    def send(self, message: bytes, host: str) -> None:
        with self.condition:
            self.__assert_running_management_thread()

            addr_port = self.host_ips[host]
            connection = self.connections[host]

            segment = connection.send(message)
            self.socket.sendto(segment.serialize(), addr_port)
