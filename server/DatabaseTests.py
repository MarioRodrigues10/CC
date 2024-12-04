from typing import Any
from unittest import TestCase, main

from common import IPOutput, IPerfOutput, PingOutput, SystemMonitorOutput
from .Database import Database

class DatabaseTests(TestCase):
    # NOTE:
    # All floating point tests must be conducted with non-repeating numbers, so that equality
    # comparisons don't fail due to lack of precision in encoding.

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.database = Database(':memory:')
        self.database.register_task('agent1', False, IPOutput('wlan0', True, 1000, 10, 2000, 15))
        self.database.register_task('agent2', True, IPerfOutput('localhost', 10.5, 100.0, 0.5))
        self.database.register_task('agent3', False, PingOutput('1.1.1.1', 15.0, 1.0))
        self.database.register_task('agent1', True, SystemMonitorOutput(1.0, 0.5))

    def test_agents(self) -> None:
        self.assertEqual(self.database.get_agent_names(), ['agent1', 'agent2', 'agent3'])

    def test_contents(self) -> None:
        tasks = self.database.get_tasks()

        # Remove None values and timestamps
        for task in tasks:
            for column, value in list(task.items()):
                if column == 'timestamp' or value is None:
                    del task[column]

        self.assertEqual(tasks, [{
                'agent': 'agent1',
                'target': 'agent1',
                'is_alert': 1,
                'command_type': 'SystemMonitorOutput',
                'cpu': 1.0,
                'memory': 0.5
            }, {
                'agent': 'agent3',
                'target': '1.1.1.1',
                'is_alert': 0,
                'command_type': 'PingOutput',
                'avg_latency': 15.0,
                'stdev_latency': 1.0
            }, {
                'agent': 'agent2',
                'target': 'localhost',
                'is_alert': 1,
                'command_type': 'IPerfOutput',
                'jitter': 10.5,
                'bandwidth': 100.0,
                'loss': 0.5
            }, {
                'agent': 'agent1',
                'target': 'agent1',
                'is_alert': 0,
                'command_type': 'IPOutput',
                'interface_name': 'wlan0',
                'connectivity': 1,
                'tx_bytes': 1000,
                'tx_packets': 10,
                'rx_bytes': 2000,
                'rx_packets': 15
            }
        ])

    def test_alert_filter(self) -> None:
        tasks = self.database.get_tasks(alerts_only=True)
        self.assertEqual(len(tasks), 2)

    def test_agent_target_filter(self) -> None:
        tasks = self.database.get_tasks(agent_target=('agent1', 'agent1'))
        self.assertEqual(len(tasks), 2)

    def test_offset_limit_filter(self) -> None:
        tasks = self.database.get_tasks(limit_offset=(2, 1))
        agents = [row['agent'] for row in tasks]
        self.assertEqual(agents, ['agent3', 'agent2'])

    def test_all_filters(self) -> None:
        tasks = self.database.get_tasks(True, ('agent1', 'agent1'), (100, 0))
        self.assertTrue('connectivity' in tasks[0])

if __name__ == '__main__':
    main()
