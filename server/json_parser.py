import json
from typing import Optional, Union

from common.structs.Command import PingCommand, IPerfCommand, IPCommand,\
    SystemMonitorCommand, TransportProtocol
from common.structs.MessageTask import MessageTask


class Parser:
    def parse_json(self, file_path:str) -> Optional[dict[str, list[MessageTask]]]:
        """
        Parses a JSON file to return a dictionary mapping device IDs to lists of MessageTask.
        """


        targets_tasks: dict[str, list[MessageTask]] = {}
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)

                for task in data["tasks"]:
                    command_data = task["command"]
                    command_type = command_data["type"]

                    command: Union[PingCommand, IPerfCommand, IPCommand, SystemMonitorCommand]

                    if command_type == "ping":
                        command = PingCommand(
                            targets=command_data["targets"],
                            count=command_data["count"],
                            rtt_alert=command_data["rttAlert"],
                        )
                    elif command_type == "iperf":
                        transport_protocol = (
                            TransportProtocol.TCP
                            if command_data["transport"] == "tcp"
                            else TransportProtocol.UDP
                        )
                        command = IPerfCommand(
                            targets=command_data["targets"],
                            transport=transport_protocol,
                            received_bytes=command_data["bytes"],
                            jitter_alert=command_data["jitterAlert"],
                            loss_alert=command_data["lossAlert"],
                            bandwidth_alert=command_data["bandwidthAlert"],
                        )
                    elif command_type == "ip":
                        command = IPCommand(
                            targets=command_data["targets"],
                            alert_down=command_data["alertDown"],
                        )
                    elif command_type == "system-monitor":
                        command = SystemMonitorCommand(
                            targets=command_data["targets"],
                            cpu_alert=command_data["cpuAlert"],
                            memory_alert=command_data["memoryAlert"],
                        )
                    else:
                        print(f"Unknown command type: {command_type}")
                        continue

                    message_task = MessageTask(
                        task_id=task["task_id"], frequency=task["frequency"], command=command
                    )

                    for device_id in task["agents"]:
                        if device_id not in targets_tasks:
                            targets_tasks[device_id] = []
                        targets_tasks[device_id].append(message_task)

                return targets_tasks

        except FileNotFoundError:
            print("File not found")
            return None
        except json.JSONDecodeError:
            print("Invalid JSON")
            return None
