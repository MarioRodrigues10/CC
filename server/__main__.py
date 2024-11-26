import sys
from pprint import pprint
from common.structs.AlertFlow import AlertFlowImpl, AlertFlow
from common import SERVER_HOST, SERVER_PORT
from .TasksParser import TasksParser


def main(argv: list[str]) -> None:
    if len(argv) != 2:
        print('Usage: python -m server <task_file>')
        sys.exit(1)

    task_file = argv[1]

    try:
        tasks = TasksParser.parse_json(task_file)
        print('Parsed Tasks:')
        pprint(tasks)
    except FileNotFoundError as e:
        print(f'Error parsing tasks file: {e}')
        sys.exit(1)

    try:
        AlertFlow.server(SERVER_HOST, SERVER_PORT, AlertFlowImpl)
    except (ConnectionError, OSError) as e:
        print(f'Error starting server: {e}')
        sys.exit(1)


if __name__ == '__main__':
    main(sys.argv)
