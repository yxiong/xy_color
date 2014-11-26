#!/usr/bin/env python
#
# Author: Ying Xiong.
# Created: Oct 28, 2014.

import math
import matplotlib.pyplot as plt

def impixelinfo(ax=None, image=None):
    """Mimic Matlab's `impixelinfo` function that shows the image pixel
    information as the cursor swipes through the figure.

    Parameters
    ----------
    ax: the axes that tracks cursor movement and prints pixel information.
        We require the `ax.images` list to be non-empty, and if more than one
        images present in that list, we examine the last (newest) one. If not
        specified, default to 'plt.gca()'.

    image: if specified, use this `image`'s pixel instead of `ax.images[-1]`'s.
        The replacement `image` must have the same dimension as `ax.images[-1]`,
        and we will still be using the `extent` of the latter when tracking
        cursor movement.

    Returns
    -------
    None

    """
    # Set default 'ax' to 'plt.gca()'.
    if not ax:
        ax = plt.gca()
    # Examine the number of images in 'ax'.
    if len(ax.images) == 0:
        print "No image in axes to visualize."
        return
    elif len(ax.images) > 1:
        print "Warning: more than one images in the axes, " + \
            "visualizing the last one."
    # Set default 'image' if not specified.
    if not image:
        image = ax.images[-1].get_array()
    # Get the 'extent' of current image.
    (left,right,bottom,top) = ax.images[-1].get_extent()

    # Re-define the 'format_coord' function and assign it to 'ax'.
    def format_coord(x, y):
        """Return a string formatting the `x`, `y` coordinates, plus additional
        image pixel information."""
        result_str = "(%.3f, %.3f): " % (x, y)
        # Get the image pixel index.
        i = int(math.floor((y - top) / (bottom - top) * image.shape[0]))
        j = int(math.floor((x - left) / (right - left) * image.shape[1]))
        # Return early if (i,j) is out of boundary.
        if (i < 0) or (i >= image.shape[0]) or (j < 0) or (j >= image.shape[1]):
            return result_str
        # Get the pixel value and add to return string.
        if (len(image.shape) == 3) and (image.shape[2] == 4):
            # 4-channel RGBA image.
            result_str += "(%.3f, %.3f, %.3f, %.3f)" % \
                          (image[i,j,0], image[i,j,1],
                           image[i,j,2], image[i,j,3])
        elif (len(image.shape) == 3) and (image.shape[2] == 3):
            # 3-channel RGB image.
            result_str += "(%.3f, %.3f, %.3f)" % \
                          (image[i,j,0], image[i,j,1], image[i,j,2])
        else:
            # Single-channel grayscale image.
            assert len(image.shape) == 2
            result_str += "%.3f" % image[i,j]
        return result_str
    ax.format_coord = format_coord

def axes_equal_3d(ax=None):
    """Mimic Matlab's `axis equal` command. The matplotlib's command
    `ax.set_aspect("equal")` only works for 2D plots, but not for 3D plots
    (those generated with `projection="3d"`).

    Parameters
    ----------
    ax: the axes whose x,y,z axis to be equalized.
        If not specified, default to `plt.gca()`.

    """
    # Set default 'ax' to 'plt.gca()'.
    if not ax:
        ax = plt.gca()

    # Get the mid-point and range for each dimension.
    def mid_and_range(lim):
        return (lim[0] + lim[1])/2.0, (lim[1] - lim[0])

    x_mid, x_range = mid_and_range(ax.get_xlim())
    y_mid, y_range = mid_and_range(ax.get_ylim())
    z_mid, z_range = mid_and_range(ax.get_zlim())

    # Set the range for each dimension to be 'max_range'.
    max_range = max(x_range, y_range, z_range)
    ax.set_xlim(x_mid - max_range/2.0, x_mid + max_range/2.0)
    ax.set_ylim(y_mid - max_range/2.0, y_mid + max_range/2.0)
    ax.set_zlim(z_mid - max_range/2.0, z_mid + max_range/2.0)
