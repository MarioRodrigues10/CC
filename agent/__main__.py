from common import (
    PingCommand,
    IPerfCommand, TransportProtocol,
    SystemMonitorCommand,
    MessageTask,
)
from .Orchestrator import Orchestrator

def main() -> None:  # Removed unused 'argv' argument
    orchestrator = Orchestrator()

    task = MessageTask(
        task_id='task-202',
        frequency=0.30,
        command=PingCommand(
            targets=['www.google.com'],
            count=5,
            rtt_alert=200.0,
        ),
    )

    task1 = MessageTask(
        task_id='task-203',
        frequency=0.20,
        command=SystemMonitorCommand(
            cpu_alert=90.0,
            memory_alert=90.0,
        ),
    )
    task2 = MessageTask(
        task_id='task-204',
        frequency=10.00,
        command=IPerfCommand(
            targets=['127.0.0.1'],  # Localhost for testing
            transport=TransportProtocol.TCP,  # TCP mode
            time=7,  # Test duration of 10 seconds
            jitter_alert=0.0,  # Jitter alert not applicable in TCP mode
            loss_alert=0.0,  # Loss alert not applicable in TCP mode
            bandwidth_alert=100.0,  # Bandwidth alert threshold (Mbps)
        ),
    )

    orchestrator.add_task(task)
    orchestrator.add_task(task1)
    orchestrator.add_task(task2)

    while True:
        r = orchestrator.get_results()
        print(r)

    try:
        orchestrator.run()
    except KeyboardInterrupt:
        print('Shutting down ...')

if __name__ == '__main__':
    main()
