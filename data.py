#!/usr/bin/env python
#
# Author: Ying Xiong.
# Created: Oct 28, 2014.

import numpy as np

# The color transform matrix from CIE XYZ space to linear sRGB space.
# Accessed from: http://www.color.org/chardata/rgb/srgb.pdf.
# Accessed on: Oct 28, 2014.
xyz_to_srgb_matrix = np.array([
    [ 3.2406, -1.5372, -0.4986],
    [-0.9689,  1.8758,  0.0415],
    [ 0.0557, -0.2040,  1.0570]
])
srgb_to_xyz_matrix = np.linalg.inv(xyz_to_srgb_matrix)

def srgb_gamma(linear_data):
    """The per-channel, nonlinear transfer function used in sRGB.
         / 12.92 * C_linear,                     if C_linear <= 0.0031308
    C = |
         \ 1.055 * C_linear ** (1/2.4) - 0.055,  otherwise
    Accessed from: http://www.color.org/chardata/rgb/srgb.pdf.
    Accessed on: Oct 28, 2014."""
    nonlinear_data = np.empty(linear_data.shape)
    part1 = (linear_data<=0.0031308)
    nonlinear_data[part1] = linear_data[part1] * 12.92
    part2 = ~part1
    nonlinear_data[part2] = 1.055 * linear_data[part2] ** (1/2.4) - 0.055
    return nonlinear_data

def read_cvrl_csv(csv_filename, empty_val = 0.0):
    """Read a csv file downloaded from cvrl.org.

    Some of the entries in the csv are empty, and will be filled with
    'empty_val'. If reading linear data, 'empty_val' should be set as 0.0, and
    if reading log data, it should be set as -np.inf.

    Returns
    -------
    An Nx4 (or sometimes Nx2) matrix, with the first column wavelength in unit
    of nm, and following columns the corresponding functions with respect to
    wavelength.

    """
    with open(csv_filename, 'r') as f:
        lines = f.readlines()
        cmfs = [[float(v or empty_val) for v in l.strip().split(',')]
                for l in lines]
        return np.array(cmfs)

def load_xyz_cmfs():
    """Load the CIE-XYZ color matching functions."""
    return read_cvrl_csv("cvrl-data/ciexyz31_1.csv")

def load_d65_spd():
    """Load the CIE D65 spectral power distribution."""
    return read_cvrl_csv("cvrl-data/Illuminantd65.csv")
