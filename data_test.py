#!/usr/bin/env python
#
# Author: Ying Xiong.
# Created: Nov 05, 2014.

import unittest

from data import *

class DataTest(unittest.TestCase):
    def test_read_cvrl_csv(self):
        # Test on reading regular data.
        cmfs = read_cvrl_csv("cvrl-data/ciexyz31_1.csv")
        self.assertAlmostEqual(cmfs[0,0], 360.0)
        self.assertAlmostEqual(cmfs[0,1], 0.000129900)
        self.assertAlmostEqual(cmfs[0,2], 0.000003917)
        self.assertAlmostEqual(cmfs[0,3], 0.000606100)

        self.assertAlmostEqual(cmfs[8,0], 368.0)
        self.assertAlmostEqual(cmfs[8,1], 0.000329388)
        self.assertAlmostEqual(cmfs[8,2], 0.000009839844)
        self.assertAlmostEqual(cmfs[8,3], 0.001543579)

        # Test on reading data with missing entries.
        cmfs = read_cvrl_csv("cvrl-data/linss2_10e_fine.csv")
        self.assertAlmostEqual(cmfs[3882,0], 778.2)
        self.assertAlmostEqual(cmfs[3882,1], 2.32643e-5)
        self.assertAlmostEqual(cmfs[3882,2], 1.82057e-6)
        self.assertAlmostEqual(cmfs[3882,3], 0.0)

        # Use -np.inf for log-scale missing entries.
        cmfs = read_cvrl_csv("cvrl-data/ss2_10e_fine.csv", -np.inf)
        self.assertAlmostEqual(cmfs[3882,0], 778.2)
        self.assertAlmostEqual(cmfs[3882,1], -4.63331)
        self.assertAlmostEqual(cmfs[3882,2], -5.73979)
        self.assertAlmostEqual(cmfs[3882,3], -np.inf)

if __name__ == "__main__":
    unittest.main()
