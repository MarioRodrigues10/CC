import sys

from common import (
    PingCommand,
    IPerfCommand, TransportProtocol,
    SystemMonitorCommand,
    MessageTask,
)
from .IPerfServer import IPerfServer
from .Orchestrator import Orchestrator

def main(argv: list[str]) -> None:
    orchestrator = Orchestrator()

    IPerfServer.start()

    other=argv[1]

    task = MessageTask(
        task_id='task-202',
        frequency=2.0,
        command=PingCommand(
            targets=[other],
            count=5,
            rtt_alert=200.0,
        ),
    )

    task1 = MessageTask(
        task_id='task-203',
        frequency=1.0,
        command=SystemMonitorCommand(
            cpu_alert=90.0,
            memory_alert=90.0,
        ),
    )
    task2 = MessageTask(
        task_id='task-204',
        frequency=5.00,
        command=IPerfCommand(
            targets=[other],  # Localhost for testing
            transport=TransportProtocol.TCP,  # TCP mode
            time=7.0,  # Test duration of 10 seconds
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

if __name__ == '__main__':
    main(sys.argv)
