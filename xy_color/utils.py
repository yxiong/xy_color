#!/usr/bin/env python
#
# Author: Ying Xiong.
# Created: Oct 22, 2014.

import numpy as np
import scipy.misc

from scipy.interpolate import interp1d

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
    xx, yy: ndarrays of the same size
        The (x,y) coordinates to be determined whether inside the horseshoe.

    horseshoe_curve: ndarray of size `Nx2`
        Each row of the matrix is an `(x,y)` coordinate for a monochromatic
        color, and the wavelength of those colors should increase from short
        (blue) to long (red) monotonically.

    Returns
    -------
    A boolean `ndarray` of the same size as `xx` and `yy`.

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
    x_from_y_12 = interp1d(horseshoe_curve[y1_index:, 1][::-1],
                           horseshoe_curve[y1_index:, 0][::-1])
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

def im2uint8(img, color_space="default"):
    """Convert the image into type `np.uint8`."""
    if color_space == "default":
        if img.dtype == np.uint8:
            return img
        elif img.dtype == np.uint16:
            return np.asarray(img / 256, np.uint8)
        elif img.dtype == np.float32 or img.dtype == np.float64:
            return np.asarray(img * 255.0, np.uint8)
        else:
            raise Exception("Unexpected image data type " + str(img.dtype))
    elif color_space == "CIE-L*a*b*":
        if img.dtype == np.uint8:
            return img
        elif img.dtype == np.float32 or img.dtype == np.float64:
            dst = np.empty(img.shape, np.uint8)
            dst[:,:,0] = img[:,:,0] * 255. / 100.
            dst[:,:,1] = img[:,:,1] + 128.
            dst[:,:,2] = img[:,:,2] + 128.
            return dst
        else:
            raise Exception("Unexpected image data type " + str(img.dtype))
    else:
        raise Exception("Unexpected color space " + color_space)

def im2float32(img, color_space="default"):
    """Convert the image into type `np.float32`."""
    if color_space == "default":
        if img.dtype == np.uint8:
            return np.asarray(img, np.float32) / 255.0
        elif img.dtype == np.uint16:
            return np.asarray(img, np.float32) / 65535.0
        elif img.dtype == np.float32 or img.dtype == np.float64:
            return np.asarray(img, np.float32)
        else:
            raise Exception("Unexpected image data type " + str(img.dtype))
    elif color_space == "CIE-L*a*b*":
        if img.dtype == np.uint8:
            dst = np.empty(img.shape, np.float32)
            dst[:,:,0] = np.asarray(img[:,:,0], "float32") / 255. * 100.
            dst[:,:,1] = np.asarray(img[:,:,1]) - 128.
            dst[:,:,2] = np.asarray(img[:,:,2]) - 128.
            return dst
        elif img.dtype == np.float32 or img.dtype == np.float64:
            return np.asarray(img, np.float32)
        else:
            raise Exception("Unexpected image data type " + str(img.dtype))
    else:
        raise Exception("Unexpected color space " + color_space)

def imread(filename, dtype=np.float32, color_space="default"):
    """Read the image from `filename` and convert it into `dtype`."""
    assert (dtype == np.float32)
    return im2float32(scipy.misc.imread(filename), color_space=color_space)

def imsave(filename, image, dtype=np.uint8, color_space="default"):
    """Convert the `image` into `dtype` before save it to `filename`."""
    assert (dtype == np.uint8)
    return scipy.misc.imsave(filename, im2uint8(image, color_space=color_space))
