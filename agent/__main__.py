import sys
import time

from common import NetTask
from .IPerfServer import IPerfServer

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

if __name__ == '__main__':
    main(sys.argv)
