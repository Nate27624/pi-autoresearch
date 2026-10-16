import unittest
import numpy as np
from data import make_digits, splits, windows

class TestData(unittest.TestCase):
    def test_pi_prefix(self):
        self.assertEqual(''.join(map(str,make_digits(100)[:15])), '141592653589793')
    def test_no_split_leakage(self):
        digits=np.arange(1000)%10
        tr,va,te=splits(digits)
        self.assertEqual((len(tr),len(va),len(te)),(800,100,100))
        x,y=windows(va,16)
        self.assertEqual(len(y),84)
        np.testing.assert_array_equal(x[0],va[:16]); self.assertEqual(y[0],va[16])
    def test_random_seed(self):
        np.testing.assert_array_equal(make_digits(100,'random',12),make_digits(100,'random',12))

if __name__=='__main__':unittest.main()
