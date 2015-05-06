#!/usr/bin/env python
#
# Author: Ying Xiong.
# Created: Apr 24, 2015.

import itertools
import numpy as np
import os
import unittest

from xy_python_utils.image_utils import imread
from xy_python_utils.unittest_utils import check_near

from color_space_transform import color_space_transform

_this_file_path = os.path.dirname(__file__)
_data_path = _this_file_path + "/data"

class ColorSpaceTransformTest(unittest.TestCase):

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

    def test_lenna(self):
        srgb = imread(_data_path + "/lenna/sRGB.png")
        srgblin = imread(_data_path + "/lenna/sRGB-linear.png")
        xyz = imread(_data_path + "/lenna/CIE-XYZ.png")
        lab = imread(_data_path + "/lenna/CIE-Lab.png",
                     color_space="CIE-L*a*b*")

        self.check_transform(srgb, srgblin, "sRGB", "sRGB-linear")
        self.check_transform(srgb, xyz, "sRGB", "CIE-XYZ")
        self.check_transform(srgb, lab, "sRGB", "CIE-L*a*b*")

    def check_transform(self, src_data, dst_data, src_space, dst_space,
                        tol = 0.02):
        cst = color_space_transform
        check_near(cst(src_data, src_space, dst_space), dst_data, tol)
        check_near(cst(dst_data, dst_space, src_space), src_data, tol)

if __name__ == "__main__":
    unittest.main()
