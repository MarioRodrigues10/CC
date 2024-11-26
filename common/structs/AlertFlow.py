import struct
import socket
import threading
from abc import ABC, abstractmethod
from typing import Optional, Type, Self


class AlertFlow(ABC):
    def __init__(self, metric: str, value: int, severity: int, timestamp: float) -> None:
        self.metric = metric
        self.value = value
        self.severity = severity
        self.timestamp = timestamp

    def serialize(self) -> bytes:
        metric_bytes = self.metric.encode('utf-8')
        value_bytes = self.value.to_bytes(8, byteorder='big')
        severity_bytes = self.severity.to_bytes(8, byteorder='big')
        timestamp_bytes = struct.pack('>d', self.timestamp)
        return b''.join([timestamp_bytes, severity_bytes, value_bytes, metric_bytes])

    @classmethod
    def deserialize(cls: Type[Self], data: bytes) -> Self:
        try:
            timestamp = struct.unpack('>d', data[:8])[0]
            severity = int.from_bytes(data[8:16], 'big')
            value = int.from_bytes(data[16:24], 'big')
            metric = data[24:].decode('utf-8')
            return cls(metric=metric, value=value, severity=severity, timestamp=timestamp)
        except (struct.error, ValueError, IndexError) as e:
            raise ValueError('Invalid data format for deserialization') from e

    def send_message(self, sock: socket.socket) -> None:
        try:
            data = self.serialize()
            sock.sendall(data)
            print(f'Sent message: {self}')
        except (socket.error, socket.timeout) as e:
            print(f'Error sending message: {e}')

    @classmethod
    def receive_message(cls: Type[Self], sock: socket.socket) -> Optional[Self]:
        try:
            buffer = bytearray()
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                buffer.extend(chunk)
            if buffer:
                return cls.deserialize(bytes(buffer))
        except (socket.error, ValueError) as e:
            print(f'Error receiving message: {e}')
        return None

    @abstractmethod
    def handle_message(self, message: Self) -> None:
        pass

    @staticmethod
    def client(host: str, port: int, alert: 'AlertFlow') -> None:
        try:
            with socket.create_connection((host, port)) as sock:
                print(f'Connected to server at {host}:{port}')
                alert.send_message(sock)
        except (ConnectionRefusedError, socket.error) as e:
            print(f'Error connecting to server: {e}')

    @staticmethod
    def server(host: str, port: int, handler_cls: Type['AlertFlow']) -> None:
        def client_handler(conn: socket.socket, addr: tuple) -> None:
            print(f'Connected by {addr}')
            try:
                alert = handler_cls.receive_message(conn)
                if alert:
                    alert.handle_message(alert)
            finally:
                conn.close()

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
                server_socket.bind((host, port))
                server_socket.listen()
                print(f'Server listening on {host}:{port}')
                while True:
                    conn, addr = server_socket.accept()
                    threading.Thread(target=client_handler, args=(conn, addr), daemon=True).start()
        except (socket.error, OSError) as e:
            print(f'Server error: {e}')

    def __str__(self) -> str:
        return (
            f'AlertFlow(metric={self.metric}, value={self.value}, '
            f'severity={self.severity}, timestamp={self.timestamp})'
        )


class AlertFlowImpl(AlertFlow):
    def handle_message(self, message: Self) -> None:
        print(f'Received message: {message}')
