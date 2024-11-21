import sys
from pprint import pprint

from .TasksParser import TasksParser

def main(argv: list[str]) -> None:
    if len(argv) != 2:
        print("Usage: python -m server <file_path>")
        sys.exit(1)

    tasks = TasksParser.parse_json(argv[1])
    pprint(tasks)

if __name__ == "__main__":
    main(sys.argv)
