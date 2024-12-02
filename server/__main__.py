import sys
from pprint import pprint

from common import NetTask
from .TasksParser import TasksParser

def main(argv: list[str]) -> None:
    if len(argv) != 2:
        print('Usage: python -m server <tasks_file>')
        sys.exit(1)

    tasks = TasksParser.parse_json(argv[1])
    pprint(tasks)

    server = NetTask('server', 9999)
    while True:
        messages, agent = server.receive()
        for m in messages:
            number = int.from_bytes(m, 'big')
            for i in range(number + 1):
                server.send(i.to_bytes(4, 'big'), agent)

        server.close(agent)

if __name__ == '__main__':
    main(sys.argv)
