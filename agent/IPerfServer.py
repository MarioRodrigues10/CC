import atexit
import subprocess
import threading

from common import CommandException

class IPerfServer:
    __process = None
    __registered_atexit = False
    __lock = threading.RLock()

    @classmethod
    def start_if_not_running(cls) -> None:
        def termination() -> None:
            try:
                cls.stop_if_running()
            except CommandException:
                pass

        with cls.__lock:
            if not cls.__registered_atexit:
                cls.__registered_atexit = True
                atexit.register(termination)

            if cls.__process is None:
                # pylint: disable-next=consider-using-with
                cls.__process = subprocess.Popen(['iperf3', '-s'],
                                                 stdout=subprocess.DEVNULL,
                                                 stderr=subprocess.DEVNULL)

    @classmethod
    def stop_if_running(cls) -> None:
        with cls.__lock:
            if cls.__process is not None:
                cls.__process.terminate()
                cls.__process.wait()
                cls.__process = None
