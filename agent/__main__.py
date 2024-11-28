import sys
import time

from common import NetTask
from .IPerfServer import IPerfServer

def main(argv: list[str]) -> None:
    if len(argv) != 3:
        print('Usage: python -m agent <agent_name> <server>')
        sys.exit(1)

    IPerfServer.start_if_not_running()

    client = NetTask(argv[1])
    client.add_host('server', (argv[2], 9999))
    while True:
        client.send(b'Hello', 'server')
        time.sleep(1)

if __name__ == '__main__':
    main(sys.argv)
