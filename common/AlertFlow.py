import socket
from threading import Thread
from typing import Optional

class AlertFlow:
    def __init__(self, bind_port: Optional[int] = None):
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if bind_port is not None:
            self.__socket.bind(('0.0.0.0', bind_port))

    def connect(self, addr: str, port: int) -> None:
        self.__socket.connect((addr, port))

    def close(self) -> None:
        self.__socket.close()

    def send(self, message: bytes) -> None:
        total_sent = 0
        while total_sent < len(message):
            sent = self.__socket.send(message[total_sent:])
            total_sent += sent

    def connection_acceptance_loop(self) -> None:
        self.__socket.listen()
        while True:
            connection, _ = self.__socket.accept()
            connection_thread = Thread(target=self.__connection_loop, args=(connection,))
            connection_thread.daemon = True
            connection_thread.start()

    def __connection_loop(self, connection: socket.socket) -> None:
        while True:
            received = connection.recv(4096)
            if received == b'':
                return # End of connetion

            self.handle_message(received)

    def handle_message(self, message: bytes) -> None:
        pass
