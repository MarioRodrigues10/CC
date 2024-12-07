#!/usr/bin/env python3

import time
import sys

from common import AlertFlow, NetTask, ALERTFLOW_DEFAULT_PORT, NETTASK_DEFAULT_PORT

MESSAGE_COUNT=10000 # 10 MiB

def alertflow_client() -> None:
    start = time.time()

    alertflow = AlertFlow('client')
    alertflow.connect('localhost', ALERTFLOW_DEFAULT_PORT)
    for _ in range(MESSAGE_COUNT):
        alertflow.send(b':)' * 500)
    alertflow.close()

    end = time.time()
    print(end - start)

def alertflow_server() -> None:
    alertflow = AlertFlow('server', ALERTFLOW_DEFAULT_PORT)
    alertflow.connection_acceptance_loop()

def nettask_client() -> None:
    start = time.time()

    nettask = NetTask('client')
    nettask.connect('server', ('localhost', NETTASK_DEFAULT_PORT))
    for _ in range(MESSAGE_COUNT):
        nettask.send(b':)' * 500, 'server')
    nettask.close()

    end = time.time()
    print(end - start)

def nettask_server() -> None:
    nettask = NetTask('server', NETTASK_DEFAULT_PORT)
    while True:
        _, _ = nettask.receive()

def main(argv: list[str]) -> None:
    fn = {
        '-uc': nettask_client,
        '-us': nettask_server,
        '-tc': alertflow_client,
        '-ts': alertflow_server
    }

    if len(argv) != 2 or argv[1] not in fn:
        print('Usage: ./test.py', '/'.join(f'[{s}]' for s in fn), file=sys.stderr)
        sys.exit(1)
    fn[argv[1]]()

if __name__ == '__main__':
    main(sys.argv)
