import threading
import time
from typing import Any
import sys

from readerwriterlock import rwlock

from common import CommandException, IPerfCommand, MessageTask, PingCommand
from .IPerfServer import IPerfServer

TIME_TO_SLEEP_AFTER_FAILED_IPERF = 1.0

class Orchestrator:
    def __init__(self) -> None:
        self.lock = rwlock.RWLockFair()
        self.buffer: list[tuple[Any, MessageTask]] = []
        self.condition = threading.Condition()

    def add_task(self, message_task: MessageTask) -> None:
        with self.lock.gen_wlock():
            thread = threading.Thread(target=self.execute_task, args=(message_task,))
            thread.daemon = True
            thread.start()

    def execute_task(self, message_task: MessageTask) -> None:
        lock: Any
        if isinstance(message_task.command, IPerfCommand):
            lock = self.lock.gen_wlock()
        else:
            lock = self.lock.gen_rlock()

        needs_to_pause_iperf = type(message_task.command) in [IPerfCommand, PingCommand]

        while True:
            if needs_to_pause_iperf:
                IPerfServer.pause()

            with lock:
                time_to_sleep = message_task.frequency
                try:
                    result = message_task.command.run()
                    with self.condition:
                        self.buffer.append((result, message_task))
                        self.condition.notify()
                except CommandException as e:
                    print(f'Ignored CommandException: {e}', file=sys.stderr)
                    if isinstance(message_task.command, IPerfCommand):
                        time_to_sleep = TIME_TO_SLEEP_AFTER_FAILED_IPERF

            if needs_to_pause_iperf:
                IPerfServer.resume()
            time.sleep(time_to_sleep)

    def get_results(self) -> tuple[Any, MessageTask]:
        with self.condition:
            while not self.buffer:
                self.condition.wait()
            return self.buffer.pop(0)
