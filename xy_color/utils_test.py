#!/usr/bin/env python
#
# Author: Ying Xiong.
# Created: Oct 23, 2014.

import numpy as np
import unittest

from data import read_cvrl_csv
from utils import *

class UtilsTest(unittest.TestCase):
    def test_xy_inside_horseshoe(self):
        # Get a horseshoe curve.
        xyz_cmfs = read_cvrl_csv("cvrl-data/ciexyz31_1.csv")
        s = np.sum(xyz_cmfs[:, 1:], axis=1)
        horseshoe_curve = np.array([xyz_cmfs[:,1]/s, xyz_cmfs[:,2]/s]).T

        # Test on a small vector.
        xx = np.array([0.05, 0.2, 0.2, 0.4, 0.6])
        yy = np.array([0.05, 0.2, 0.6, 0.2, 0.8])
        inside = xy_inside_horseshoe(xx, yy, horseshoe_curve)
        self.assertEqual(xx.shape, inside.shape)
        self.assertTrue(inside[1])
        self.assertTrue(inside[2])
        self.assertTrue(inside[3])
        self.assertFalse(inside[0])
        self.assertFalse(inside[4])

        # Test on regular grid.
        (xx,yy) = np.meshgrid(np.linspace(0,1,101), np.linspace(0,1,101))
        inside = xy_inside_horseshoe(xx, yy, horseshoe_curve)
        self.assertTrue(inside[20, 20])
        self.assertTrue(inside[20, 40])
        self.assertTrue(inside[60, 20])
        self.assertFalse(inside[0, 0])
        self.assertFalse(inside[10, 5])
        self.assertFalse(inside[60, 60])
        self.assertFalse(inside[80, 80])

    def test_normalize_rows_and_columns(self):
        matrix = np.random.rand(3, 5)
        row_normalized = normalize_rows(matrix)
        self.assertEqual(row_normalized.shape, (3,5))
        self.assertTrue(np.max(np.abs(
            np.sum(row_normalized, axis=1) - np.array([1,1,1]))) < 0.0001)
        col_normalized = normalize_columns(matrix)
        self.assertEqual(col_normalized.shape, (3,5))
        self.assertTrue(np.max(np.abs(
            np.sum(col_normalized, axis=0) - np.array([1,1,1,1,1]))) < 0.0001)

if __name__ == "__main__":
    unittest.main()
