import sys

from threading import Thread
from typing import Any

from common import (
    AlertFlow, NetTask,
    Message, MessageTask, MessageTasksRequest, SerializationException,
    ALERTFLOW_DEFAULT_PORT, NETTASK_DEFAULT_PORT
)

from .Database import Database, DatabaseException
from .HTTPBackend import HTTPBackend
from .TasksParser import TasksParser

class ServerAlertFlowHandler(AlertFlow):
    def __init__(self, *args: Any, database: Database):
        self.__database = database
        super().__init__(*args)

    def handle_message(self, message: bytes, host: str) -> None:
        try:
            message_deserilized = Message.deserialize(message)
            self.__database.register_task(host, True, message_deserilized)
        except SerializationException as e:
            print(f'Ignoring SerializationException: {e}', file=sys.stderr)
        except DatabaseException as e:
            print(f'Ignoring DatabaseException: {e}', file=sys.stderr)

def handle_nettask_message(tasks: dict[str, list[MessageTask]],
                           database: Database,
                           nettask: NetTask,
                           message_bytes: bytes,
                           agent: str) -> None:
    try:
        message = Message.deserialize(message_bytes)

        if isinstance(message, MessageTasksRequest):
            if agent in tasks:
                for task in tasks[agent]:
                    nettask.send(task.serialize(), agent)
                print(f'Sent tasks to {agent}')
            else:
                print(f'Ignoring MessageTasksRequest from unknown agent {agent}',
                      file=sys.stderr)
                nettask.close(agent)
        else:
            database.register_task(agent, False, message)
    except SerializationException as e:
        print(f'Ignoring SerializationException: {e}', file=sys.stderr)
    except DatabaseException as e:
        print(f'Ignoring DatabaseException: {e}', file=sys.stderr)

def main(argv: list[str]) -> None:
    if len(argv) != 3:
        print('Usage: python -m server <tasks_file> <database_file>')
        sys.exit(1)

    tasks_file = argv[1]
    database_file = argv[2]

    tasks = TasksParser.parse_json(tasks_file)
    database = Database(database_file)

    http_backend = HTTPBackend(database)
    http_thread = Thread(target = http_backend.serve)
    http_thread.daemon = True
    http_thread.start()

    nettask = NetTask('server', NETTASK_DEFAULT_PORT)
    alertflow = ServerAlertFlowHandler('server', ALERTFLOW_DEFAULT_PORT, database=database)
    alertflow_thread = Thread(target = alertflow.connection_acceptance_loop)
    alertflow_thread.daemon = True
    alertflow_thread.start()

    print('Waiting for agent requests')
    while True:
        messages, agent = nettask.receive()
        for message in messages:
            handle_nettask_message(tasks, database, nettask, message, agent)

if __name__ == '__main__':
    main(sys.argv)
