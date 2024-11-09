import Command
class MessageTask:
    def __init__(self, taskId: str, frequency: float, command: Command):
        self.taskId = taskId
        self.frequency = frequency
        self.command = command

    def serialize(self) -> bytes:
        taskId_bytes = self.taskId.encode('utf-8')
        frequency_bytes = self.frequency.to_bytes(8, 'big')
        command_bytes = self.command.serialize()
        return b"".join([frequency_bytes, taskId_bytes, command_bytes])
    
    def deserialize(cls, data: bytes):
        taskId, frequency, command = data.split(b',')
        
        taskId = taskId.decode('utf-8')
        frequency = float.fromhex(frequency.decode('utf-8'))
        command = Command.deserialize(command)
        
        return cls(taskId=taskId, frequency=frequency, command=command)
    