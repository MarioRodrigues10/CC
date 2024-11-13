class MessageRegister:
    def __init__(self, id: str):
        self.id = id

    def serialize(self) -> bytes:
        id_bytes = self.id.encode('utf-8')
        return id_bytes
    
    def deserialize(cls, data: bytes):
        id = data.decode('utf-8')
        
        return cls(id=id)