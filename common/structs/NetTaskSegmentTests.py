from unittest import TestCase, main

from .. import NetTaskSegment, NetTaskDataSegmentBody, NetTaskAckSegmentBody

class NetTaskSegmentTests(TestCase):
    def test_data(self) -> None:
        initial_segment = NetTaskSegment(1, 'host', NetTaskDataSegmentBody(b'1234'))
        segment_bytes = initial_segment.serialize()
        final_segment = NetTaskSegment.deserialize(segment_bytes)

        self.assertEqual(initial_segment, final_segment)

    def test_ack(self) -> None:
        initial_segment = NetTaskSegment(100, 'localhost', NetTaskAckSegmentBody(420))
        segment_bytes = initial_segment.serialize()
        final_segment = NetTaskSegment.deserialize(segment_bytes)

        self.assertEqual(initial_segment, final_segment)

if __name__ == '__main__':
    main()
