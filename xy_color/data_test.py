#!/usr/bin/env python
#
# Author: Ying Xiong.
# Created: Nov 05, 2014.

import unittest

import numpy as np

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

    def test_load_fw(self):
        # Load CIE-XYZ color matching functions.
        xyz_cmfs, wl = load_fw("xyz-cmfs")
        self.assertTrue(np.max(np.abs(wl - np.arange(360, 831))) < 1.0e-5)
        self.assertEqual(xyz_cmfs.shape[0], 3)
        self.assertAlmostEqual(xyz_cmfs[0,8], 0.000329388)
        self.assertAlmostEqual(xyz_cmfs[1,8], 0.000009839844)
        self.assertAlmostEqual(xyz_cmfs[2,8], 0.001543579)

        # Load CIE-D65 spectral power distribution with given wavelength list.
        d65_spd, _ = load_fw("d65-spd", wl)
        self.assertEqual(len(d65_spd), len(wl))
        self.assertAlmostEqual(d65_spd[8], 50.998900)

    def test_d65(self):
        # Compute the xy coordinates of d65, and check with ground truth.
        xyz_cmfs, wl = load_fw("xyz-cmfs")
        d65_spd, _ = load_fw("d65-spd", wl)
        d65_xyz = np.dot(xyz_cmfs, d65_spd)
        d65_xy = (d65_xyz / np.sum(d65_xyz))[:2]
        self.assertAlmostEqual(d65_xy[0], 0.3127, places=4)
        self.assertAlmostEqual(d65_xy[1], 0.3290, places=4)

    def test_srgb(self):
        # Check the normalized xyz chromaticity coordinates of RGB and white
        # point.
        def check_normalized_xyz(xyz, n_xyz, places):
            self.assertAlmostEqual(np.sum(n_xyz), 1.0)
            xyz /= np.sum(xyz)
            self.assertAlmostEqual(xyz[0], n_xyz[0], places=places)
            self.assertAlmostEqual(xyz[1], n_xyz[1], places=places)
            self.assertAlmostEqual(xyz[2], n_xyz[2], places=places)
        check_normalized_xyz(np.dot(srgb_to_xyz_matrix, np.array([1,0,0])),
                             srgb_red_xyz, 3)
        check_normalized_xyz(np.dot(srgb_to_xyz_matrix, np.array([0,1,0])),
                             srgb_green_xyz, 3)
        check_normalized_xyz(np.dot(srgb_to_xyz_matrix, np.array([0,0,1])),
                             srgb_blue_xyz, 3)
        check_normalized_xyz(np.dot(srgb_to_xyz_matrix, np.array([1,1,1])),
                             srgb_white_xyz, 4)

    def test_adobe(self):
        # Make sure the matrices convert to and from XYZ colorspace are invert
        # of each other.
        err = np.dot(xyz_to_adobe_matrix, adobe_to_xyz_matrix) - np.eye(3)
        self.assertAlmostEqual(np.max(np.abs(err)), 0.0, places=4)
        err = np.dot(icc_pcs_to_adobe_matrix, adobe_to_icc_pcs_matrix)-np.eye(3)
        self.assertAlmostEqual(np.max(np.abs(err)), 0.0, places=4)

        # Check the xy chromaticity coordinates of RGB and white point.
        def check_xy(c_xyz, c_xy):
            s = np.sum(c_xyz)
            self.assertAlmostEqual(c_xyz[0]/s, c_xy[0], places=4)
            self.assertAlmostEqual(c_xyz[1]/s, c_xy[1], places=4)
        check_xy(np.dot(adobe_to_xyz_matrix, np.array([1,0,0])), adobe_red_xy)
        check_xy(np.dot(adobe_to_xyz_matrix, np.array([0,1,0])), adobe_green_xy)
        check_xy(np.dot(adobe_to_xyz_matrix, np.array([0,0,1])), adobe_blue_xy)
        check_xy(np.dot(adobe_to_xyz_matrix, np.array([1,1,1])), adobe_white_xy)

        # Check that the (normalized) white point should match CIE D65.
        wp_xyz = np.dot(adobe_to_xyz_matrix, np.array([95.047, 100.00, 108.883]))
        norm_wp_xyz = adobe_abs_to_norm_xyz(wp_xyz)
        norm_wp_xyz = adobe_abs_to_norm_xyz(np.array([95.047, 100.00, 108.883]))
        norm_wp_xyz = np.array([95.047, 100.00, 108.883])
        norm_wp_xy = norm_wp_xyz / np.sum(norm_wp_xyz)
        self.assertAlmostEqual(norm_wp_xy[0], 0.3127, places=4)
        self.assertAlmostEqual(norm_wp_xy[1], 0.3290, places=4)

if __name__ == "__main__":
    unittest.main()
