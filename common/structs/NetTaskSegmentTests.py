from unittest import TestCase, main

from .. import NetTaskSegment, NetTaskDataSegmentBody, NetTaskAckSegmentBody

class NetTaskSegmentTests(TestCase):
    # NOTE:
    # All floating point tests must be conducted with non-repeating numbers, so that equality
    # comparisons don't fail due to lack of precision in encoding.

    def test_data(self) -> None:
        initial_segment = NetTaskSegment(1, 1.0, 'host', NetTaskDataSegmentBody(b'1234'))
        segment_bytes = initial_segment.serialize()
        final_segment = NetTaskSegment.deserialize(segment_bytes)

        self.assertEqual(initial_segment, final_segment)

    def test_ack(self) -> None:
        initial_segment = NetTaskSegment(100, 1.5, 'localhost', NetTaskAckSegmentBody(420))
        segment_bytes = initial_segment.serialize()
        final_segment = NetTaskSegment.deserialize(segment_bytes)

        self.assertEqual(initial_segment, final_segment)

if __name__ == '__main__':
    main()
