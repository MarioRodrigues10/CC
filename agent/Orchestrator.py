import threading
import time
from readerwriterlock import rwlock

from common import (
    IPerfCommand,
    MessageTask,
)

from .IPerfServer import IPerfServer


class Orchestrator:
    def __init__(self)-> None:
        self.lock = rwlock.RWLockFairD()
        self.tasks : dict[str,MessageTask]= {} # type: ignore
        self.threads : list[threading.Thread]=[]

    def add_task(self, message_task: MessageTask) -> None:
        with self.lock.gen_wlock():
            self.tasks[message_task.task_id] = message_task
            thread = threading.Thread(target=self.execute_task, args=(message_task,))
            self.threads.append(thread)
            print(f"Task {message_task.task_id} added")

    def execute_task(self, message_task: MessageTask) -> None:
        if isinstance(message_task.command, IPerfCommand):
            while True:
                with self.lock.gen_wlock():
                    IPerfServer.stop_if_running()
                    result = message_task.command.run()
                    IPerfServer.start_if_not_running()
                    print(f"Result: {result}")
                time.sleep(1)
        else:
            while True:
                with self.lock.gen_rlock():
                    result = message_task.command.run()
                    print(f"Result: {result}")
                time.sleep(message_task.frequency)

    def start(self) -> None:
        for thread in self.threads:
            thread.start()

    def run(self) -> None:
        for thread in self.threads:
            thread.join()
