import common
from server.json_parser import parser

def main() -> None:
    print(common.SERVER_MESSAGE)

    json_parser = parser()

    data = json_parser.parse_json()
    
    if data is None:
        print("Error parsing JSON file")
        return
    
    for device_id, tasks in data.items():
        print(f"Device ID: {device_id}")
        for task in tasks:
            print(f"  Task ID: {task.task_id}, Frequency: {task.frequency}")

if __name__ == '__main__':
    main()
