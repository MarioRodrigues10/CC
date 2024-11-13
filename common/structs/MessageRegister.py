class MessageRegister:
    def __init__(self, message_id: str):
        self.message_id = message_id

    def serialize(self) -> bytes:
        id_bytes = self.message_id.encode('utf-8')
        return id_bytes

    def deserialize(self, cls, data: bytes):
        message_id = data.decode('utf-8')

        return cls(message_id=message_id)
