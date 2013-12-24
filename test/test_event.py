
import unittest
try:
    import unittest.mock as mock
except ImportError:
    import mock

from event import UnifiedEventSelector


class TestUnifiedEventSelector(unittest.TestCase):
    def test_priority(self):
        a = UnifiedEventSelector()
        a.queue_event(10, "stuff", {})
        a.queue_event(10, "things", {"index":2})
        a.queue_event(8, "things", {"index":3})
        self.assertEqual(next(a), (8, "things", {"index":3}))
        self.assertEqual(next(a), (10, "stuff", {}))
        self.assertEqual(next(a), (10, "things", {"index":2}))
        self.assertRaises(StopIteration, next, a)

    def test_instant(self):
        a = UnifiedEventSelector()
        a.instant_event("things", {"index":2})
        a.instant_event("things", {"index":3})
        self.assertEqual(next(a), (0, "things", {"index":2}))
        self.assertEqual(next(a), (0, "things", {"index":3}))
        self.assertRaises(StopIteration, next, a)

    def test_generator_distribution(self):
        a = UnifiedEventSelector()
        Mock = unittest.mock.Mock
        g1 = Mock()
        g1.next = Mock(return_value=(10, "g1", {}))
        a.add_generator(g1)
        g2 = Mock()
        g2.next = Mock(return_value=(1, "g2", {}))
        a.add_generator(g2)

        g1_count = 0
        g2_count = 0
        total_time = 0
        TRIALS = 10000
        for _ in range(TRIALS):
            time, event, _ = next(a)
            if event == "g1":
                g1_count += 1
            elif event == "g2":
                g2_count += 1
            else:
                self.fail("invalid event")

        ratio = (g1_count * 1.0 / g2_count)
        self.assertAlmostEqual(ratio, 10.0/1.0, delta=1, msg="Bad generator event ratio")
        expected_time = TRIALS / 11.0
        self.assertAlmostEqual(time, expected_time, delta=expected_time/10, msg="Bad generator time results")

    def test_mixed(self):
        a = UnifiedEventSelector()
        Mock = unittest.mock.Mock
        g1 = Mock()
        g1.next = Mock(return_value=(1, "c", {}))
        a.add_generator(g1)
        a.queue_event(100000, "d", {})
        a.instant_event("a", {})
        a.queue_event(0.00001, "b", {})

        sim = (event for time, event, params in a)
        from itertools import islice
        self.assertEqual(list(islice(sim, 4)), ["a", "b", "c", "c"])
