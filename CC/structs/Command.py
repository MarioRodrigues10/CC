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
    def __init__(self, targets, transport, bytes, jitter_alert, loss_alert, bandwidth_alert):
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
        return b"".join([targets_bytes, transport_bytes, bytes_bytes, jitter_alert_bytes, loss_alert_bytes, bandwidth_alert_bytes])

    def deserialize(cls, data: bytes):
        targets, transport, bytes, jitter_alert, loss_alert, bandwidth_alert = data.split(b',')
        
        targets = targets.decode('utf-8')
        transport = transport.decode('utf-8')
        bytes = int.from_bytes(bytes, 'big')
        jitter_alert = int.from_bytes(jitter_alert, 'big') / cls.SCALE
        loss_alert = int.from_bytes(loss_alert, 'big') / cls.SCALE
        bandwidth_alert = int.from_bytes(bandwidth_alert, 'big') / cls.SCALE
        
        return cls(targets=targets, transport=transport, bytes=bytes, jitter_alert=jitter_alert, loss_alert=loss_alert, bandwidth_alert=bandwidth_alert)

class IPCommand:
    def __init__(self, targets, alert_down):
        self.targets = targets
        self.alert_down = alert_down
        
    def serialize(self) -> bytes:
        targets_bytes = self.targets.encode('utf-8')
        alert_down_bytes = self.alert_down.to_bytes(1, 'big')
        return b','.join([targets_bytes, alert_down_bytes])
    
    def deserialize(cls, data: bytes):
        targets, alert_down = data.split(b',')
        
        targets = targets.decode('utf-8')
        alert_down = alert_down.decode('utf-8')
        
        return cls(targets=targets, alert_down=alert_down)


class SystemMonitorCommand:
    def __init__(self, targets, cpu_alert, memory_alert):
        self.targets = targets
        self.cpu_alert = cpu_alert
        self.memory_alert = memory_alert

    def serialize(self) -> bytes:
        targets_bytes = self.targets.encode('utf-8')
        cpu_alert_bytes = self.cpu_alert.to_bytes(8, 'big')
        memory_alert_bytes = self.memory_alert.to_bytes(8, 'big')
        return b','.join([targets_bytes, cpu_alert_bytes, memory_alert_bytes])
    
    def deserialize(cls, data: bytes):
        targets, cpu_alert, memory_alert = data.split(b',')
        
        targets = targets.decode('utf-8')
        cpu_alert = float.from_bytes(cpu_alert, 'big')
        memory_alert = float.from_bytes(memory_alert, 'big')
        
        return cls(targets=targets, cpu_alert=cpu_alert, memory_alert=memory_alert)
