#!/usr/bin/env python
#
# Author: Ying Xiong.
# Created: Oct 22, 2014.

import numpy as np
import matplotlib.pyplot as plt

from scipy.interpolate import interp1d

from data import *

def color_space_xyy_to_xyz(src_data):
    """Convert data from CIE-xyY color space to CIE-XYZ color space."""
    assert src_data.shape[0] == 3, "Input data must be 3xN matrix."
    dst_data = np.zeros(src_data.shape)
    # Y = Y.
    dst_data[1,:] = src_data[2,:]
    # X = Y / y * x.
    validTag = src_data[1,:] > 0
    dst_data[0,validTag] = src_data[2,validTag] / src_data[1,validTag] * \
                           src_data[0,validTag]
    # Z = Y / y * (1 - x - y).
    dst_data[2,validTag] = src_data[2,validTag] / src_data[1,validTag] * \
                           (1 - src_data[0,validTag] - src_data[1,validTag])
    return dst_data

def color_space_xyz_to_xyy(src_data):
    """Convert data from CIE-XYZ color space to CIE-xyY color space."""
    assert src_data.shape[0] == 3, "Input data must be 3xN matrix."
    dst_data = np.zeros(src_data.shape)
    # Y = Y.
    dst_data[2] = src_data[1,:]
    # x = X / (X + Y + Z).
    # y = Y / (X + Y + Z).
    s = np.sum(src_data, axis = 0)
    validTag = s > 0
    dst_data[:2, validTag] = src_data[:2,validTag] / s[validTag]
    return dst_data

def color_space_transform(src_data, src_space, dst_space):
    """Transform an image from a one color space to another color space.

    Parameters
    ----------
    src_data: the input data to be transformed.
        The data can be 'ndarray' of either one of following form:
        1. a 3xN matrix, with each column representing a color vector.
        2. an MxNx3 or MxNx4 image. The alpha channel will be preserved if
           present.

    src_space, dst_space: color spaces to be transformed from and to.
        Current supported color spaces are:
        "CIE-XYZ", "CIE-xyY", "sRGB-linear" and "sRGB".

    Returns
    -------
    dst_data: the output data after transformation. It will be an 'ndarray' of
        the same size as 'src_data.

    """
    if len(src_data.shape) == 3:
        # The 'src_data' is an image, convert it into 3xN color matrix.
        (M,N,C) = src_data.shape
        assert (C == 3) or (C == 4)
        src_data2 = src_data[:,:,:3].reshape(M*N, 3).T

        # Recursively call this function on the 3xN matrix.
        dst_data2 = color_space_transform(src_data2, src_space, dst_space)

        # Put the transformed data back into image form.
        dst_data = np.zeros(src_data.shape)
        dst_data[:,:,:3] = dst_data2.T.reshape(M,N,3)
        if (C == 4):
            dst_data[:,:,3] = src_data[:,:,3]
        return dst_data

    # Do the color space transform on a 3xN color matrix.
    if (src_space == "CIE-xyY" and dst_space == "CIE-XYZ"):
        dst_data = color_space_xyy_to_xyz(src_data)
    elif (src_space == "CIE-XYZ" and dst_space == "CIE-xyY"):
        dst_data = color_space_xyz_to_xyy(src_data)
    elif (src_space == "CIE-XYZ" and dst_space == "sRGB-linear"):
        dst_data = np.dot(xyz_to_srgb_matrix, src_data)
    elif (src_space == "sRGB-linear" and dst_space == "CIE-XYZ"):
        dst_data = np.dot(srgb_to_xyz_matrix, src_data)
    elif (src_space == "sRGB-linear" and dst_space == "sRGB"):
        dst_data = srgb_gamma(src_data)
    else:
        raise Exception("Unknown transform from '%s' to '%s'." %
                        (src_space, dst_space))
    return dst_data

def normalize_rows(matrix):
    """Normalize the input matrix such that each row of the result matrix sums
    to one.

    """
    assert len(matrix.shape) == 2
    s = np.sum(matrix, axis = 1)
    return matrix / np.tile(s, (matrix.shape[1], 1)).T

def normalize_columns(matrix):
    """Normalize the input matrix such that each column of the result matrix
    sums to one.

    """
    assert len(matrix.shape) == 2
    return matrix / np.sum(matrix, axis = 0)

def xy_inside_horseshoe(xx, yy, horseshoe_curve):
    """Check whether a set of coordinates are inside the horseshoe shape.

    Parameters
    ----------
    xx, yy : ndarrays of the same size
        The (x,y) coordinates to be determined whether inside the horseshoe.

    horseshoe_curve : an Nx2 matrix
        Each row of the matrix is an (x,y) coordinate for a monochromatic color,
        and the wavelength of those colors should increase from short (blue) to
        long (red) monotonically.

    Returns
    -------
    An ndarray of the same size as 'xx' and 'yy'.

    """
    # We assume the 'y' component of the curve is composed of a monotonically
    # increasing part from starting point y0 to maximum y1, followed by a
    # monotonically decreasing part from maximum y1 to end point y2. We also
    # assume the starting point y0 is smaller than end point y2. These
    # conditions will be satisfied if the curve starts from short wavelength
    # (blue) to long wavelength (red).
    y0 = horseshoe_curve[0,1]
    y1_index = np.argmax(horseshoe_curve[:,1])
    y1 = horseshoe_curve[y1_index,1]
    y2 = horseshoe_curve[-1,1]
    assert y0 < y2

    # The following interpolation functions will compute an 'x' value given a
    # 'y' value for each portion of the horseshoe curve. The last one is a line
    # connecting two end points.
    x_from_y_01 = interp1d(horseshoe_curve[:y1_index+1, 1],
                           horseshoe_curve[:y1_index+1, 0])
    x_from_y_12 = interp1d(horseshoe_curve[y1_index:, 1],
                           horseshoe_curve[y1_index:, 0])
    x_from_y_02 = interp1d(horseshoe_curve[np.ix_([0,-1], [1])].flatten(),
                           horseshoe_curve[np.ix_([0,-1], [0])].flatten())

    # Given a (x,y) point whose y coordinate is between y0 and y1, we compute
    # its horizontal intersection (xl, xr) to the horseshoe. The point is inside
    # the horseshoe if xl < x < xr. The calculation of 'xr' depends on whether y
    # is bigger or smaller than y2.
    assert xx.shape == yy.shape
    inside = np.zeros(xx.shape, "bool")
    # Lower part of the horseshoe: y0 < y <= y2.
    y0_y2_mask = np.logical_and(y0 < yy, yy <= y2)
    xx_between_y0_y2 = xx[y0_y2_mask]
    yy_between_y0_y2 = yy[y0_y2_mask]
    xl_between_y0_y2 = x_from_y_01(yy_between_y0_y2)
    xr_between_y0_y2 = x_from_y_02(yy_between_y0_y2)
    inside[y0_y2_mask] = np.logical_and(xl_between_y0_y2 < xx_between_y0_y2,
                                        xx_between_y0_y2 < xr_between_y0_y2)
    # Upper part of the horseshoe: y2 < y < y1.
    y2_y1_mask = np.logical_and(y2 < yy, yy < y1)
    xx_between_y2_y1 = xx[y2_y1_mask]
    yy_between_y2_y1 = yy[y2_y1_mask]
    xl_between_y2_y1 = x_from_y_01(yy_between_y2_y1)
    xr_between_y2_y1 = x_from_y_12(yy_between_y2_y1)
    inside[y2_y1_mask] = np.logical_and(xl_between_y2_y1 < xx_between_y2_y1,
                                        xx_between_y2_y1 < xr_between_y2_y1)

    return inside
