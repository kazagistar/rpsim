
import unittest

from ratearray import RateArray

class TestRateArray(unittest.TestCase):
    def test_sum(self):
        a = RateArray("event", 3)
        a[0] = 2
        a[1] = 3
        a[2] = 5
        rate, _, _ = a.next()
        self.assertEqual(rate, 10)

