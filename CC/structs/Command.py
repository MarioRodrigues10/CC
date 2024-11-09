class PingCommand:
    SCALE = 1_000_000
    def __init__(self, targets: list, count: int, rtt_alert: float):
        self.targets = targets
        self.count = count
        self.rtt_alert = rtt_alert

    def serialize(self) -> bytes:
        targets_bytes = self.targets.encode('utf-8')
        count_bytes = self.count.to_bytes(8, 'big')
        rtt_alert_bytes = int(self.rtt_alert * self.SCALE).to_bytes(8, 'big')
        return b"".join([count_bytes, rtt_alert_bytes, targets_bytes])
    
    def deserialize(cls, data: bytes):
        count = int.from_bytes(data[:8], 'big')
        rtt_alert = int.from_bytes(data[8:16], 'big') / cls.SCALE
        targets = data[16:].decode('utf-8')

        return cls(targets=targets, count=count, rtt_alert=rtt_alert)


class IPerfCommand:
    SCALE = 1_000_000
    def __init__(self, targets: list, transport: str, bytes: float, jitter_alert: float, loss_alert: float, bandwidth_alert: float):
        self.targets = targets
        self.transport = transport
        self.bytes = bytes
        self.jitter_alert = jitter_alert
        self.loss_alert = loss_alert
        self.bandwidth_alert = bandwidth_alert

    def serialize(self) -> bytes:    
        targets_bytes = self.targets.encode('utf-8')
        transport_bytes = self.transport.encode('utf-8')
        bytes_bytes = self.bytes.to_bytes(8, 'big')
        jitter_alert_bytes = int(self.jitter_alert * self.SCALE).to_bytes(8, 'big')
        loss_alert_bytes = int(self.loss_alert * self.SCALE).to_bytes(8, 'big')
        bandwidth_alert_bytes = int(self.bandwidth_alert * self.SCALE).to_bytes(8, 'big')
        return b"".join([bytes_bytes, jitter_alert_bytes, loss_alert_bytes, bandwidth_alert_bytes, targets_bytes, transport_bytes])

    def deserialize(cls, data: bytes):
        bytes = int.from_bytes(data[:8], 'big')
        jitter_alert = int.from_bytes(data[8:16], 'big') / cls.SCALE
        loss_alert = int.from_bytes(data[16:24], 'big') / cls.SCALE
        bandwidth_alert = int.from_bytes(data[24:32], 'big') / cls.SCALE
        targets = data[32:40].decode('utf-8')
        transport = data[40:].decode('utf-8')
                
        return cls(targets=targets, transport=transport, bytes=bytes, jitter_alert=jitter_alert, loss_alert=loss_alert, bandwidth_alert=bandwidth_alert)

class IPCommand:
    def __init__(self, targets: list, alert_down: bool):
        self.targets = targets
        self.alert_down = alert_down
        
    def serialize(self) -> bytes:
        targets_bytes = self.targets.encode('utf-8')
        alert_down_bytes = self.alert_down.to_bytes(1, 'big')
        return b"".join([alert_down_bytes, targets_bytes])
    
    def deserialize(cls, data: bytes):        
        targets = targets.decode(data[1:])
        alert_down = alert_down.decode(data[:1])
        
        return cls(targets=targets, alert_down=alert_down)


class SystemMonitorCommand:
    SCALE = 1_000_000
    def __init__(self, targets: list, cpu_alert: float, memory_alert: float):
        self.targets = targets
        self.cpu_alert = cpu_alert
        self.memory_alert = memory_alert

    def serialize(self) -> bytes:
        targets_bytes = self.targets.encode('utf-8')
        cpu_alert_bytes = int(self.cpu_alert * self.SCALE).to_bytes(8, 'big')   
        memory_alert_bytes = int(self.memory_alert * self.SCALE).to_bytes(8, 'big')
        return b"".join([cpu_alert_bytes, memory_alert_bytes, targets_bytes])
    
    def deserialize(cls, data: bytes):

        cpu_alert = int.from_bytes(data[:8], 'big') / cls.SCALE
        memory_alert = int.from_bytes(data[8:16], 'big') / cls.SCALE
        targets = data[16:].decode('utf-8')        
        
        return cls(targets=targets, cpu_alert=cpu_alert, memory_alert=memory_alert)
