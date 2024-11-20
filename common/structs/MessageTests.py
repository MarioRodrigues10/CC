from unittest import TestCase, main

from .. import \
    Message, IPOutput, IPerfOutput, PingOutput, SystemMonitorOutput, MessagePrepare, MessageRegister

class MessageTests(TestCase):
    # NOTE:
    # All floating point tests must be conducted with non-repeating numbers, so that equality
    # comparisons don't fail due to lack of precision in encoding.

    def test_ip_output(self) -> None:
        initial_message = IPOutput('wlan0', True, 1000, 10, 20000, 200)
        message_bytes = initial_message.serialize()
        final_message = Message.deserialize(message_bytes)

        self.assertEqual(initial_message, final_message)

    def test_iperf_output(self) -> None:
        initial_message = IPerfOutput('1.1.1.1', 1.25, 1002.0, 0.5)
        message_bytes = initial_message.serialize()
        final_message = Message.deserialize(message_bytes)

        self.assertEqual(initial_message, final_message)

    def test_ping_output(self) -> None:
        initial_message = PingOutput('9.9.9.9', 10.125, 1.5)
        message_bytes = initial_message.serialize()
        final_message = Message.deserialize(message_bytes)

        self.assertEqual(initial_message, final_message)

    def test_system_monitor_output(self) -> None:
        initial_message = SystemMonitorOutput(20.125, 40.5)
        message_bytes = initial_message.serialize()
        final_message = Message.deserialize(message_bytes)

        self.assertEqual(initial_message, final_message)

    def test_message_prepare(self) -> None:
        initial_message = MessagePrepare(True, False)
        message_bytes = initial_message.serialize()
        final_message = Message.deserialize(message_bytes)

        self.assertEqual(initial_message, final_message)

    def test_message_register(self) -> None:
        initial_message = MessageRegister('myrouter')
        message_bytes = initial_message.serialize()
        final_message = Message.deserialize(message_bytes)

        self.assertEqual(initial_message, final_message)

if __name__ == '__main__':
    main()
