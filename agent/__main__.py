from .IPerfServer import IPerfServer

def main() -> None:
    IPerfServer.start_if_not_running()
    input('Press return to terminate the iperf server ...')

if __name__ == '__main__':
    main()
