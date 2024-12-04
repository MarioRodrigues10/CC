import atexit
import os
import signal
import subprocess
import threading
from typing import cast

import inotify_simple

from common import CommandException

class IPerfServer:
    __process = None
    __lock = threading.RLock()
    __paused = False

    @classmethod
    def start(cls) -> None:
        def termination() -> None:
            try:
                cls.__wait_for_tests_to_finish()
                if cls.__process is not None:
                    cls.__process.terminate()
                    cls.__process.wait()
            except CommandException:
                pass

        with cls.__lock:
            atexit.register(termination)

            if cls.__process is None:
                # pylint: disable-next=consider-using-with
                cls.__process = subprocess.Popen(['iperf3', '-s'],
                                                 stdout=subprocess.DEVNULL,
                                                 stderr=subprocess.DEVNULL)

    @classmethod
    def __wait_for_tests_to_finish(cls) -> None:
        try:
            sockets = []
            fd_dir = f'/proc/{cast(subprocess.Popen, cls.__process).pid}/fd'
            for fd in os.listdir(fd_dir):
                fd_path = os.path.join(fd_dir, fd)
                fd_link = os.readlink(fd_path)

                if fd_link.startswith('socket:'):
                    sockets.append(fd_path)

            if len(sockets) <= 1:
                return

            inotify = inotify_simple.INotify()
            for socket in sockets:
                inotify.add_watch(socket, inotify_simple.masks.CLOSE)

            inotify.read()
        except OSError:
            pass

    @classmethod
    def pause(cls) -> None:
        with cls.__lock:
            if cls.__process is not None and not cls.__paused:
                cls.__wait_for_tests_to_finish()
                cls.__process.send_signal(signal.SIGSTOP)
                cls.__paused = True

    @classmethod
    def resume(cls) -> None:
        with cls.__lock:
            if cls.__process is not None and cls.__paused:
                cls.__process.send_signal(signal.SIGCONT)
                cls.__paused = False
