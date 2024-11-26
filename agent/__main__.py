from common.structs.AlertFlow import AlertFlowImpl
from common import SERVER_HOST, SERVER_PORT

def main() -> None:
    alert = AlertFlowImpl(metric='Memory_Usage', value=92, severity=3, timestamp=1679234.56)

    try:
        AlertFlowImpl.client(SERVER_HOST, SERVER_PORT, alert)
    except ConnectionError as e:
        print(f'Error sending alert: {e}')

if __name__ == '__main__':
    main()
