import sys
from socket import gethostname
from threading import Thread

from common import (
    AlertFlow, NetTask,
    Message, MessageTask, MessageTasksRequest, SerializationException,
    ALERTFLOW_DEFAULT_PORT, NETTASK_DEFAULT_PORT
)

from .IPerfServer import IPerfServer
from .Orchestrator import Orchestrator

def task_end_monitor(alertflow: AlertFlow, nettask: NetTask, orchestrator: Orchestrator) -> None:
    while True:
        results, task = orchestrator.get_results()
        messages = []

        if isinstance(results, dict):
            messages = list(results.values())
        else:
            messages = [results]

        for message in messages:
            if task.command.should_emit_alert(message):
                alertflow.send(message.serialize())
            else:
                nettask.send(message.serialize(), 'server')

def main(argv: list[str]) -> None:
    if len(argv) != 2:
        print('Usage: python -m agent <server_address>')
        sys.exit(1)

    server_address = argv[1]

    IPerfServer.start()
    orchestrator = Orchestrator()

    nettask = NetTask(gethostname())
    nettask.connect('server', (server_address, NETTASK_DEFAULT_PORT))
    nettask.send(MessageTasksRequest().serialize(), 'server')

    alertflow = AlertFlow(gethostname())
    alertflow.connect(server_address, ALERTFLOW_DEFAULT_PORT)

    task_end_thread = Thread(target=task_end_monitor, args=(alertflow, nettask, orchestrator))
    task_end_thread.daemon = True
    task_end_thread.start()

    while True:
        messages, _ = nettask.receive()

        for message_bytes in messages:
            try:
                message = Message.deserialize(message_bytes)
                if isinstance(message, MessageTask):
                    print(f'Received task {message.task_id}')
                    orchestrator.add_task(message)
                else:
                    message_type = type(message).__name__
                    print(f'Received wrong message type: {message_type}', file=sys.stderr)
            except SerializationException as e:
                print(f'Ignoring SerializationException: {e}', file=sys.stderr)

if __name__ == '__main__':
    main(sys.argv)
