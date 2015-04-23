#!/usr/bin/env python
#
# Author: Ying Xiong.
# Created: Oct 23, 2014.

import itertools
import numpy as np
import unittest

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

    def test_color_space_transform(self):
        # CIE-xyY to CIE-XYZ.
        src_data = np.array([[0.5, 0.5, 1.0],
                             [0.3, 0.2, 2.0],
                             [0.0, 0.0, 0.0]]).T
        dst_data = color_space_transform(src_data, "CIE-xyY", "CIE-XYZ")
        self.assertTrue(np.all(np.abs(
            dst_data - np.array([[1.0, 1.0, 0.0],
                                 [3.0, 2.0, 5.0],
                                 [0.0, 0.0, 0.0]]).T) < 1.0e-3))

        # CIE-XYZ to CIE-xyY.
        src_data2 = color_space_transform(dst_data, "CIE-XYZ", "CIE-xyY")
        self.assertTrue(np.all(np.abs(src_data - src_data2) < 1.0e-3))

        # CIE-XYZ to sRGB-linear.
        src_data = np.array([[1.0, 2.0, 3.0],
                             [0.3127, 0.3290, 0.3583],   # reference white.
                             [0.0, 0.0, 0.0]]).T
        dst_data = color_space_transform(src_data, "CIE-XYZ", "sRGB-linear")
        self.assertTrue(np.all(np.abs(
            dst_data - np.array([[-1.3296, 2.9072, 2.8187],
                                 [0.3290, 0.3290, 0.3290],
                                 [0.0, 0.0, 0.0]]).T) < 1.0e-3))

        # sRGB-linear to sRGB.
        src_data = np.array([[1.0, 1.0, 1.0],
                             [0.0031308, 0.1, 0.5],
                             [0.0, 0.0, 0.0]]).T
        dst_data = color_space_transform(src_data, "sRGB-linear", "sRGB")
        self.assertTrue(np.all(np.abs(
            dst_data - np.array([[1.0, 1.0, 1.0],
                                 [0.0401, 0.3492, 0.7354],
                                 [0.0, 0.0, 0.0]]).T) < 1.0e-3))

        # Check the image version.
        (xx,yy) = np.meshgrid(np.linspace(0, 1, 5), np.linspace(0, 1, 8))
        zz = 1.0 - xx - yy
        src_image = np.zeros((8, 5, 4))
        src_image[:,:,0] = xx
        src_image[:,:,1] = yy
        src_image[:,:,2] = zz
        src_image[:,:,3] = xx + yy + zz

        dst_image = color_space_transform(src_image, "CIE-XYZ", "sRGB-linear")

        for i,j in itertools.product(xrange(8), xrange(5)):
            dst_pixel = color_space_transform(
                np.array([xx[i,j], yy[i,j], zz[i,j]]),
                "CIE-XYZ", "sRGB-linear")
            for c in xrange(3):
                self.assertAlmostEqual(dst_image[i,j,c], dst_pixel[c])
            self.assertEqual(dst_image[i,j,3], src_image[i,j,3])

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
