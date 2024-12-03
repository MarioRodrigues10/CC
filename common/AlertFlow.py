import socket
from threading import Thread
from typing import Optional

class AlertFlowException(Exception):
    pass

class AlertFlow:
    def __init__(self, bind_port: Optional[int] = None):
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if bind_port is not None:
            self.__socket.bind(('0.0.0.0', bind_port))

    def connect(self, addr: str, port: int) -> None:
        self.__socket.connect((addr, port))

    def close(self) -> None:
        self.__socket.close()

    def __construct_segment(self, message: bytes) -> bytes:
        length_bytes = (len(message) + 2).to_bytes(2, 'big')
        return length_bytes + message

    def send(self, message: bytes) -> None:
        segment = self.__construct_segment(message)

        total_sent = 0
        while total_sent < len(segment):
            sent = self.__socket.send(segment[total_sent:])
            total_sent += sent

    def connection_acceptance_loop(self) -> None:
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
                message = self.__receive_fixed_length(connection, segment_length - 2)

                self.handle_message(message)
        except AlertFlowException:
            pass

    def handle_message(self, message: bytes) -> None:
        pass
