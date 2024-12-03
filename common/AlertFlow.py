import socket
import sys
from threading import Thread, RLock
from typing import Optional, cast

class AlertFlowException(Exception):
    pass

class AlertFlow:
    def __init__(self, own_host_name: str, bind_port: Optional[int] = None):
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__own_host_name = own_host_name
        if bind_port is not None:
            self.__socket.bind(('0.0.0.0', bind_port))

        self.__connected_addr: Optional[str] = None
        self.__connected_port: Optional[int] = None
        self.__lock = RLock()

    def connect(self, addr: str, port: int) -> None:
        with self.__lock:
            self.__socket.connect((addr, port))
            self.__connected_addr = addr
            self.__connected_port = port

    def close(self) -> None:
        with self.__lock:
            self.__socket.close()

    def __construct_segment(self, message: bytes) -> bytes:
        own_host_name_bytes = self.__own_host_name.encode('utf-8') + b'\0'
        segment_length = len(message) + len(own_host_name_bytes) + 2
        length_bytes = segment_length.to_bytes(2, 'big')

        return length_bytes + own_host_name_bytes + message

    def __reconnect(self) -> None:
        while True:
            try:
                try:
                    self.__socket.close()
                except OSError:
                    pass

                self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.connect(cast(str, self.__connected_addr), cast(int, self.__connected_port))
                return
            except OSError:
                pass

    def send(self, message: bytes) -> None:
        segment = self.__construct_segment(message)

        with self.__lock:
            total_sent = 0
            while total_sent < len(segment):
                sent = self.__socket.send(segment[total_sent:])
                if sent == 0:
                    # NOTE: this needs to be tested in CORE
                    self.__reconnect()
                total_sent += sent

    def connection_acceptance_loop(self) -> None:
        with self.__lock:
            self.__socket.listen()
            while True:
                connection, _ = self.__socket.accept()
                connection_thread = Thread(target=self.__connection_loop, args=(connection,))
                connection_thread.daemon = True
                connection_thread.start()

    def __receive_fixed_length(self, connection: socket.socket, length: int) -> bytes:
        total_received = b''
        remaining_bytes = length
        while remaining_bytes > 0:
            received = connection.recv(remaining_bytes)
            if received == b'':
                raise AlertFlowException('Connection ended')

            total_received += received
            remaining_bytes -= len(received)

        return total_received

    def __connection_loop(self, connection: socket.socket) -> None:
        try:
            while True:
                segment_length = int.from_bytes(self.__receive_fixed_length(connection, 2), 'big')
                remaining_segment = self.__receive_fixed_length(connection, segment_length - 2)

                try:
                    host_end = remaining_segment.index(b'\0')
                    host = remaining_segment[:host_end].decode('utf-8')
                    message = remaining_segment[host_end + 1:]
                except (UnicodeError, ValueError):
                    print('Closing AlertFlow connection due to invalid state', file=sys.stderr)
                    connection.shutdown(socket.SHUT_RDWR)
                    connection.close()
                    return

                self.handle_message(message, host)
        except AlertFlowException:
            pass

    def handle_message(self, message: bytes, host: str) -> None:
        pass
