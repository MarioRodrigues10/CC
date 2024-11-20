from unittest import TestCase, main

from .. import \
    Command, PingCommand, SystemMonitorCommand, IPerfCommand, IPCommand, TransportProtocol

class CommandTest(TestCase):
    def test_ping(self) -> None:
        initial_command = PingCommand(['localhost', '1.1.1.1'], 10, 100.0)
        command_bytes = initial_command.serialize()
        final_command = Command.deserialize(command_bytes)

        self.assertEqual(initial_command, final_command)

    def test_system_monitor(self) -> None:
        initial_command = SystemMonitorCommand(50.0, 100.0)
        command_bytes = initial_command.serialize()
        final_command = Command.deserialize(command_bytes)

        self.assertEqual(initial_command, final_command)

    def test_iperf(self) -> None:
        initial_command = IPerfCommand( \
            ['localhost', '1.1.1.1'], \
            TransportProtocol.TCP, \
            1000, 100.0, 10.0, 1000)
        command_bytes = initial_command.serialize()
        final_command = Command.deserialize(command_bytes)

        self.assertEqual(initial_command, final_command)

    def test_ip(self) -> None:
        initial_command = IPCommand(['wlan0', 'eth0'], True)
        command_bytes = initial_command.serialize()
        final_command = Command.deserialize(command_bytes)

        self.assertEqual(initial_command, final_command)

if __name__ == '__main__':
    main()
