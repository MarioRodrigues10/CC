import sys
from pprint import pprint

from common import AlertFlow, IPOutput, IPerfOutput, PingOutput, SystemMonitorOutput
from .Database import Database
from .TasksParser import TasksParser
from .HTTPBackend import HTTPBackend

class AlertFlowImpl(AlertFlow):
    def handle_message(self, message: bytes, host: str) -> None:
        print(f'Received message: {message!r} from {host}')

def main(argv: list[str]) -> None:
    if len(argv) != 2:
        print('Usage: python -m server <tasks_file>')
        sys.exit(1)

    tasks = TasksParser.parse_json(argv[1])
    pprint(tasks)

    database = Database('server.sqlite')
    print('Database created')
    # Insert tasks into database
    database.register_task('agent1', False, IPOutput('wlan0', True, 1000, 10, 2000, 15))
    database.register_task('agent2', True, IPerfOutput('localhost', 10.5, 100.0, 0.5))
    database.register_task('agent3', False, PingOutput('1.1.1.1', 15.0, 1.0))
    database.register_task('agent1', True, SystemMonitorOutput(1.0, 0.5))

    HTTPBackend(database).serve()
    print('HTTP server started')

    alertflow = AlertFlowImpl('server', 10000)
    alertflow.connection_acceptance_loop()

    print('AlertFlow started')

    # server = NetTask('server', 9999)
    # while True:
    #     messages, agent = server.receive()
    #     for m in messages:
    #         number = int.from_bytes(m, 'big')
    #         for i in range(number + 1):
    #             server.send(i.to_bytes(4, 'big'), agent)
    #
    #     server.close(agent)

if __name__ == '__main__':
    main(sys.argv)
