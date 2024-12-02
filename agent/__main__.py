import sys

from common import (
    PingCommand,
    IPerfCommand, TransportProtocol,
    SystemMonitorCommand,
    MessageTask,
)

from common import NetTask

from .IPerfServer import IPerfServer
from .Orchestrator import Orchestrator

def main(argv: list[str]) -> None:
    if len(argv) != 3:
        print('Usage: python -m agent <agent_name> <server>')
        sys.exit(1)

    IPerfServer.start_if_not_running()

    number = int(input('Write a positive number> '))

    client = NetTask(argv[1])
    client.connect('server', (argv[2], 9999))
    client.send(number.to_bytes(4, 'big'), 'server')
    while True:
        messages, host = client.receive()
        if host == '':
            break

        for m in messages:
            print(int.from_bytes(m, 'big'))

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
        task_id='task-203',
        frequency=2.00,
        command=IPerfCommand(
            targets=['127.0.0.1'],  # Localhost for testing
            transport=TransportProtocol.TCP,  # TCP mode
            time=10,  # Test duration of 10 seconds
            jitter_alert=0.0,  # Jitter alert not applicable in TCP mode
            loss_alert=0.0,  # Loss alert not applicable in TCP mode
            bandwidth_alert=100.0,  # Bandwidth alert threshold (Mbps)
        ),
    )
    orchestrator.add_task(task)
    orchestrator.add_task(task1)
    orchestrator.add_task(task2)

    orchestrator.start()

    try:
        orchestrator.run()
    except KeyboardInterrupt:
        print('Shutting down ...')

if __name__ == '__main__':
    main(sys.argv)
