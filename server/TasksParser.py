import json
from typing import Any

from common import (
    Command,
    PingCommand,
    IPerfCommand, TransportProtocol,
    IPCommand,
    SystemMonitorCommand,
    MessageTask
)

class TasksParserException(Exception):
    pass

class TasksParser:
    @staticmethod
    def __assert_condition(condition: bool) -> None:
        if not condition:
            raise TasksParserException('JSON of tasks doesn\'t match schema')

    @classmethod
    def __assert_type(cls, value: Any, type_name: type) -> None:
        cls.__assert_condition(isinstance(value, type_name))

    @classmethod
    def __assert_list(cls, lst: Any, type_name: type) -> None:
        cls.__assert_type(lst, list)
        for e in lst:
            cls.__assert_type(e, type_name)

    @classmethod
    def __assert_dict(cls, dictionary: Any, keys: dict[str, type]) -> None:
        cls.__assert_type(dictionary, dict)
        cls.__assert_condition(set(dictionary.keys()) == set(keys.keys()))
        for key, typ in keys.items():
            cls.__assert_type(dictionary[key], typ)

    @classmethod
    def __parse_ping_command(cls, command_data: Any) -> PingCommand:
        cls.__assert_dict(command_data, {
            'type': str,
            'targets': list,
            'count': int,
            'rttAlert': float
        })
        cls.__assert_list(command_data['targets'], str)

        return PingCommand(
            command_data['targets'],
            command_data['count'],
            command_data['rttAlert'],
        )

    @classmethod
    def __parse_iperf_command(cls, command_data: Any) -> IPerfCommand:
        cls.__assert_dict(command_data, {
            'type': str,
            'targets': list,
            'transport': str,
            'time': float,
            'jitterAlert': float,
            'lossAlert': float,
            'bandwidthAlert': float
        })
        cls.__assert_list(command_data['targets'], str)
        cls.__assert_condition(command_data['transport'] in ['tcp', 'udp'])

        transport_protocol = \
            TransportProtocol.TCP if command_data['transport'] == 'tcp' else TransportProtocol.UDP

        return IPerfCommand(
            command_data['targets'],
            transport_protocol,
            command_data['time'],
            command_data['jitterAlert'],
            command_data['lossAlert'],
            command_data['bandwidthAlert'],
        )

    @classmethod
    def __parse_ip_command(cls, command_data: Any) -> IPCommand:
        cls.__assert_dict(command_data, {
            'type': str,
            'targets': list,
            'alertDown': bool
        })
        cls.__assert_list(command_data['targets'], str)

        return IPCommand(command_data['targets'], command_data['alertDown'])

    @classmethod
    def __parse_system_monitor_command(cls, command_data: Any) -> SystemMonitorCommand:
        cls.__assert_dict(command_data, {
            'type': str,
            'cpuAlert': float,
            'memoryAlert': float
        })

        return SystemMonitorCommand(command_data['cpuAlert'], command_data['memoryAlert'])

    @classmethod
    def parse_json(cls, file_path: str) -> dict[str, list[MessageTask]]:
        targets_tasks: dict[str, list[MessageTask]] = {}
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            cls.__assert_dict(data, { 'tasks': list })
            for task in data['tasks']:
                cls.__assert_dict(task, {
                    'task_id': str,
                    'frequency': float,
                    'agents': list,
                    'command': dict
                })
                cls.__assert_list(task['agents'], str)
                cls.__assert_condition('type' in task['command'])

                command_data = task['command']
                command_type = command_data['type']

                command: Command

                if command_type == 'ping':
                    command = cls.__parse_ping_command(command_data)
                elif command_type == 'iperf':
                    command = cls.__parse_iperf_command(command_data)
                elif command_type == 'ip':
                    command = cls.__parse_ip_command(command_data)
                elif command_type == 'system-monitor':
                    command = cls.__parse_system_monitor_command(command_data)
                else:
                    cls.__assert_condition(False)

                message_task = MessageTask(task['task_id'], task['frequency'], command)

                for device_id in task['agents']:
                    if device_id not in targets_tasks:
                        targets_tasks[device_id] = []
                    targets_tasks[device_id].append(message_task)

            return targets_tasks
        except (OSError, json.JSONDecodeError, KeyError) as e:
            raise TasksParserException() from e
