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

def adjust_wl(fw_in, wl_in, wl_out):
    """Adjust the wavelength list of the input function(s)."""
    # For multiple functions, do the adjustment on each one of them and
    # concatenate results together.
    if len(fw_in.shape) > 1:
        fw_out_list = []
        for k in xrange(fw_in.shape[0]):
            fw_out_list.append(adjust_wl(fw_in[k], wl_in, wl_out))
        return np.vstack(fw_out_list)
    # Do the adjustment for a single wavelength function.
    assert (wl_in[1] - wl_in[0]) == (wl_out[1] - wl_out[0])
    dw = wl_in[1] - wl_in[0]
    left_index = int(np.round((wl_out[0] - wl_in[0]) / dw))
    right_index = int(np.round((wl_out[-1] - wl_in[-1]) / dw))
    # The result contains three parts (two pads and a center).
    left_pad = np.zeros(0)
    center = fw_in
    right_pad = np.zeros(0)
    # Compute left pad.
    if left_index < 0:
        left_pad = np.zeros(-left_index)
    else:
        center = center[left_index:]
    # Compute right pad.
    if right_index >= 0:
        right_pad = np.zeros(right_index)
    else:
        center = center[:right_pad]
    return np.concatenate((left_pad, center, right_pad))

def load_fw(name, wl=None):
    """Load function of wavelength.

    Parameters
    ----------
    name: a string for the name of function.
          "xyz-cmfs": CIE-XYZ color matching functions.
          "d65-spd": CIE-D65 spectral power distribution.

    wl: wavelength list, optional.

    Returns
    -------
    fw: the loaded function(s) of wavelength.

    wl: the wavelength list.
        It will be the same as input `wl` if it is not `None`, or will be loaded
        together with `fw` as input data.
    """
    # Load the 'fw' and corresponding 'load_wl'.
    if name == "xyz-cmfs":
        csv_data = read_cvrl_csv("cvrl-data/ciexyz31_1.csv")
        load_wl = csv_data[:,0]
        fw = csv_data[:, 1:].T
    elif name == "d65-spd":
        csv_data = read_cvrl_csv("cvrl-data/Illuminantd65.csv")
        load_wl = csv_data[:,0]
        fw = csv_data[:,1]
    else:
        raise Exception("Unknown name '%s' for `load_fw`." % name)
    # Adjust the 'wl' if provided as input.
    if wl is not None:
        return (adjust_wl(fw, load_wl, wl), wl)
    else:
        return (fw, load_wl)

def get_blackbody_spd(temperature, wl):
    """Get blackbody radiation spectral power distribution.
    """
    # Setup constants.
    h = 6.6260695729e-34    # Planck constant.
    c = 299792458           # Speed of light.
    k = 1.380648813e-23     # Boltzmann constant.
    # Compute SPD by Planck's law.
    wl = wl * 1e-9
    spd = 2*h*(c**2) / np.power(wl,5) / (np.exp(h*c/wl/k/temperature) - 1)
    # Normalize the spd such that it sums to 1.
    return spd / np.sum(spd)
