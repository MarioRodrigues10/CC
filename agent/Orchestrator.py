import threading
import time
from readerwriterlock import rwlock

from common import (
    IPerfCommand,
    MessageTask,
    CommandException,
)

from .IPerfServer import IPerfServer

class Orchestrator:
    def __init__(self) -> None:
        self.lock = rwlock.RWLockFairD()
        self.tasks: dict[str, MessageTask] = {}
        self.threads: list[threading.Thread] = []
        self.buffer: list[str] = []
        self.condition = threading.Condition()

    def add_task(self, message_task: MessageTask) -> None:
        with self.lock.gen_wlock():
            self.tasks[message_task.task_id] = message_task
            thread = threading.Thread(target=self.execute_task, args=(message_task,))
            thread.daemon = True
            thread.start()
            self.threads.append(thread)
            print(f"Task {message_task.task_id} added")

    def execute_task(self, message_task: MessageTask) -> None:
        if isinstance(message_task.command, IPerfCommand):
            while True:
                try:
                    with self.lock.gen_wlock():
                        IPerfServer.stop_if_running()
                        result = str(message_task.command.run())  # Serialize result
                        with self.condition:
                            self.buffer.append(result)
                            print("IPERF normal")
                            self.condition.notify()
                except CommandException as e:
                    result = str(e)  # Capture the exception as a string
                    print("IPERF exception")
                finally:
                    IPerfServer.start_if_not_running()
                time.sleep(message_task.frequency)
        else:
            while True:
                with self.lock.gen_rlock():
                    try:
                        result = str(message_task.command.run())  # Serialize result
                        with self.condition:
                            self.buffer.append(result)
                            self.condition.notify()
                    except CommandException as e:
                        result = str(e)  # Capture the exception as a string
                time.sleep(message_task.frequency)

    def start(self) -> None:
        for thread in self.threads:
            thread.start()

    def run(self) -> None:
        for thread in self.threads:
            thread.join()

    def get_results(self) -> str:  # Update if returning single result
        with self.condition:
            while not self.buffer:
                self.condition.wait()
            return self.buffer.pop(0)
