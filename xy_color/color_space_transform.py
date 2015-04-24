#!/usr/bin/env python
#
# Author: Ying Xiong.
# Created: Apr 24, 2015.

import numpy as np
import sys

from data import *

def color_space_transform(src_data, src_space, dst_space):
    """Transform an image from a one color space to another color space.

    Parameters
    ----------
    src_data: ndarray
        The input data to be transformed, of either one of following form:
          1. a `3xN` matrix, with each column representing a color vector.
          2. an `MxNx3` or `MxNx4` image. The alpha channel will be preserved if
             present.

    src_space, dst_space: string
        Color spaces to be transformed from and to. Current supported color
        spaces are: `"CIE-XYZ"`, `"CIE-xyY"`, `"sRGB-linear"` and `"sRGB"`.

    Returns
    -------
    dst_data : ndarray
        The output data after transformation. It will be an `ndarray` of
        the same size as `src_data`.

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

    try:
        # Find a transform function from `src_space` to `dst_space` and run it.
        _src_space = _color_space_name[src_space]
        _dst_space = _color_space_name[dst_space]
        _transform_fcn = getattr(
            sys.modules[__name__],
            "_transform_%s_to_%s" % (_src_space, _dst_space))
        return _transform_fcn(src_data)
    except AttributeError:
        # There is no such transform function defined. In this case we will use
        # an intermediate space `itm_space`, try convert the data from
        # `src_space` to `itm_space` and then from `itm_space` to `dst_space`.
        if src_space == "sRGB" or dst_space == "sRGB":
            itm_space = "sRGB-linear"
        else:
            itm_space = "CIE-XYZ"
        if src_space == itm_space or dst_space == itm_space:
            raise Exception("Unknown transform from '%s' to '%s'." %
                            (src_space, dst_space))
        itm_data = color_space_transform(src_data, src_space, itm_space)
        dst_data = color_space_transform(itm_data, itm_space, dst_space)
        return dst_data

_color_space_name = {
    "CIE-XYZ": "xyz",
    "CIE-xyY": "xyy",
    "sRGB": "srgb",
    "sRGB-linear": "srgblin",
}

def _transform_xyy_to_xyz(src_data):
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

def _transform_xyz_to_xyy(src_data):
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

def _transform_xyz_to_srgblin(src_data):
    return np.dot(xyz_to_srgb_matrix, src_data)

def _transform_srgblin_to_xyz(src_data):
    return np.dot(srgb_to_xyz_matrix, src_data)

def _transform_srgblin_to_srgb(src_data):
    return srgb_gamma(src_data)

def _transform_srgb_to_srgblin(src_data):
    return srgb_inverse_gamma(src_data)
